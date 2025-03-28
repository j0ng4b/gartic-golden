import abc
import base64
import socket
import threading
import zlib


class BaseClient(abc.ABC):
    def __init__(self, address, port):
        if address is None or port is None:
            raise ValueError('server address and port must be set')

        self.room = None
        self.room_clients = {}
        
        # Estado do jogo
        self.name = 'Player'

        self.draw_theme = None
        self.draw_object = None
        self.words = []

        # Contexto de execução, armazena informações de execução de cada thread
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((socket.gethostbyname(address), int(port)))

        self.mutex = threading.Lock()
        self.msgs = {
            '': [],
        }

        self.error = None

    def start(self):
        # Inicia o a comunicação com o servidor, deve ser inciado antes de
        # qualquer coisa devido a pilha de mensagem
        thread = threading.Thread(target=self.handle_messages)
        thread.daemon = True
        thread.start()

        self.server_register()


    ###
    ### Métodos de comunicação: manipulação e análise de mensagens
    ###
    def handle_messages(self):
        while True:
            msg = self.socket.recv(1024).decode()

            # Verifica se a mensagem está no formato correto
            if '/' not in msg or ':' not in msg:
                print('Mensagem inválida:', msg)
                continue


            threading.Thread(
                target=self.parser_message,
                args=(msg,)
            ).start()

    def parser_message(self, msg):
        dest, msg = msg.split('/')
        msg_type, args = msg.split(':')
        args = args.split(';')


        # Verifica se a mensagem é uma resposta
        if msg_type == 'RESP':
            with self.mutex:
                self.msgs[dest].append(args[0])

            return

        # Verifica se a mensagem veio do servidor
        if dest == '':
            self.parse_server_message(msg_type, args)

        # Verifica se a mensagem veio de um cliente
        if dest in self.room_clients:
            response = self.parse_client_message(dest, msg_type, args)
            if response is not None:
                self.send_message('RESP', response, dest=dest, wait_response=False)

    def parse_server_message(self, msg_type, args):
        if msg_type == 'CONNECT':
            with self.mutex:
                self.msgs[args[0]] = []

            self.room_clients[args[0]] = {
                'name': None,
                'msgs': [],
                'state': None,
                'score': 0,
                'self': False,
            }

            self.room_clients[args[0]]['name'] = self.send_message('GREET', dest=args[0])

        elif msg_type == 'DISCONNECT':
            with self.mutex:
                del self.msgs[args[0]]

            del self.room_clients[args[0]]
        elif msg_type == 'PLAY':
            pass
        elif msg_type == 'GAME':
            pass

        return None

    def parse_client_message(self, dest, msg_type, args):
        if msg_type == 'GREET':
            return self.name

        elif msg_type == 'CHAT':
            with self.mutex:
                self.room_clients[dest]['msgs'].append(args[0])

            self.handle_chat(self.room_clients[dest], args[0])

        elif msg_type == 'GUESS':
            if self.room_clients.get(args[0]) is None:
                return 'Cliente não encontrado'

            elif self.room_clients[dest]['state'] == 'guess':
                return 'Palpite já foi dado'

            elif self.room_clients[dest]['state'] == 'skip':
                return 'Cliente não pode mais dar palpites'

            elif self.room_clients[dest]['state'] == 'draw':
                return 'Cliente é quem está desenhando'


            if args[0] == self.draw_object:
                self.client_got_the_right_answer(dest)

                self.room_clients[dest]['state'] = 'guess'
                self.room_clients[dest]['score'] += 5

                return 'OK'

            return 'Palpite está incorreto'

        elif msg_type == 'GTRA':
            if self.room_clients.get(args[0]) is None:
                return 'Cliente não encontrado'

            elif self.room_clients[dest]['state'] == 'guess':
                return 'Cliente já acertou o palpite'

            elif self.room_clients[dest]['state'] == 'skip':
                return 'Cliente não pode mais dar palpites'

            elif self.room_clients[dest]['state'] == 'draw':
                return 'Cliente é quem está desenhando'

            self.room_clients[dest]['state'] = 'guess'
            self.room_clients[dest]['score'] += 5
            return 'OK'

        elif msg_type == 'SKIP':
            if self.room_clients.get(args[0]) is None:
                return 'Cliente não encontrado'

            elif self.room_clients[dest]['state'] == 'guess':
                return 'Cliente já acertou o palpite'

            elif self.room_clients[dest]['state'] == 'skip':
                return 'Cliente já não pode mais dar palpites'

            elif self.room_clients[dest]['state'] == 'draw':
                return 'Cliente é quem está desenhando'

            self.room_clients[dest]['state'] = 'skip'
            return 'OK'

        elif msg_type == 'DRAW':
            if self.room_clients.get(args[0]) is None:
                return 'Cliente não encontrado'

            elif self.room_clients[dest]['state'] == 'draw':
                return 'Cliente já está desenhando'

            self.room_clients[dest]['state'] = 'draw'
            if self.room_clients[dest]['self']:
                self.handle_draw()

            return 'OK'

        elif msg_type == 'FDRAW':
            # Reseta o estado de todos os clientes
            for client in self.room_clients.keys():
                if self.room_clients[client]['state'] == 'draw':
                    # Calcula a pontuação do cliente que estava desenhando
                    if args[0] == 'all-guess':
                        self.room_clients[client]['score'] += 8
                    elif args[0] == 'guess':
                        self.room_clients[client]['score'] += 5
                    else:  # timeout
                        self.room_clients[client]['score'] += 0

                self.room_clients[client]['state'] = None

        elif msg_type == 'CANVAS':
            # Decodifica a imagem e envia para o método de tratamento
            canvas_data = base64.b64decode(args[0])
            canvas_data = zlib.decompress(canvas_data)
            self.handle_canvas(canvas_data)

        elif msg_type == 'SCORE':
            if self.room_clients.get(args[0]) is None:
                return 'Cliente não encontrado'

            return self.room_clients[dest]['score']

        return None

    @abc.abstractmethod
    def handle_chat(self, client, message):
        raise NotImplementedError('handle_chat must be implemented')

    @abc.abstractmethod
    def handle_draw(self):
        raise NotImplementedError('handle_draw must be implemented')

    @abc.abstractmethod
    def handle_canvas(self, canvas):
        raise NotImplementedError('handle_canvas must be implemented')


    ###
    ### Métodos principais para comunicação
    ###
    def get_message(self, dest):
        while True:
            with self.mutex:
                if len(self.msgs[dest]) == 0:
                    continue

                return self.msgs[dest].pop(0)

    def send_message(self, type, *args, dest='', wait_response=True):
        self.socket.send(f"{dest}/{type}:{';'.join(args)}".encode())

        if not wait_response:
            return None
        return self.get_message(dest)

    def get_server_error(self):
        error = self.error
        self.error = None

        return error


    ###
    ### Métodos de comunicação com o servidor
    ###
    def server_register(self):
        res = self.send_message('REGISTER', self.name)
        if res is not None and res.startswith('OK'):
            self.room_clients[res.split('&')[1]] = {
                'name': self.name,
                'msgs': [],
                'state': None,
                'score': 0,
                'self': True,
            }

            return True

        self.error = res
        return False

    def server_unregister(self):
        res = self.send_message('UNREGISTER')
        if res == 'OK':
            return True

        self.error = res
        return False

    def server_create_room(self, room_type, room_name, theme, max_rouds, room_password=None):
        args = [room_type, room_name, theme, max_rouds]
        if room_password is not None:
            args.append(room_password)

        res = self.send_message('ROOM', *args)

        if res is not None and res.isdigit():
            self.room = res
            return True

        self.error = res
        return False

    def server_close_room(self):
        res = self.send_message('CROOM')
        if res == 'OK':
            return True

        self.error = res
        return False

    def server_list_rooms(self, room_type=None):
        args = []
        if room_type is not None:
            args.append(room_type)

        res = self.send_message('LIST', *args)

        rooms = None
        if res is not None and res.find('\n'):
            rooms = res.split('\n')
        return rooms

    def server_enter_room(self, room_code, room_password=None):
        args = [room_code]
        if room_password is not None:
            args.append(room_password)

        res = self.send_message('ENTER', *args)
        if res == 'OK':
            self.room = room_code
            return True

        self.error = res
        return False

    def server_leave_room(self):
        res = self.send_message('LEAVE')
        if res == 'OK':
            self.room = None
            self.room_clients = dict(list(self.room_clients.items())[:1])
            return True

        self.error = res
        return False


    ###
    ### Métodos de comunicação com outros clientes
    ###
    def client_chat(self, message):
        for client in self.room_clients.keys():
            self.send_message('CHAT', message, dest=client, wait_response=False)

    def client_guess(self, guess):
        self_client = None
        response = None

        for client_id, client in self.room_clients.items():
            if client['state'] == 'draw':
                response = self.send_message('GUESS', guess, dest=client_id)

                if response == 'OK' and self_client is not None:
                    self_client['state'] = 'guess'
                    return True

            if client['self']:
                if response is not None:
                    if response == 'OK':
                        client['state'] = 'guess'
                        return True

                    self.error = response
                    return False

                self_client = client

        self.error = response
        return False

    def client_draw(self, client):
        for room_client in self.room_clients.keys():
            self.send_message('DRAW', client, dest=room_client, wait_response=False)

    def client_finish_draw(self, reason):
        for client in self.room_clients.keys():
            self.send_message('FDRAW', reason, dest=client, wait_response=False)

    def client_skip(self):
        for client in self.room_clients.keys():
            self.send_message('SKIP', dest=client, wait_response=False)

    def client_got_the_right_answer(self, client):
        for room_client in self.room_clients.keys():
            self.send_message('GTRA', client, dest=room_client, wait_response=False)

    def client_canvas(self, canvas_data):
        # Comprime a imagem e envia para todos os clientes
        canvas_data = zlib.compress(canvas_data)
        canvas_data = base64.b64encode(canvas_data).decode()

        for client in self.room_clients.keys():
            self.send_message('CANVAS', canvas_data, dest=client, wait_response=False)

    def client_score(self):
        scores = []
        for client in self.room_clients.keys():
            response = self.send_message('SCORE', dest=client)

            if response is not None and response.isdigit():
                scores.append(int(response))

        freq = {}
        for score in scores:
            freq[score] = freq.get(score, 0) + 1

        return max(freq, key=lambda x: freq[x])

