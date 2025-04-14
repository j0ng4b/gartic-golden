import abc
import base64
import json
import socket
import threading
import zlib


class BaseClient(abc.ABC):
    def __init__(self, address, port):
        if address is None or port is None:
            raise ValueError('server address and port must be set')

        self.room = None
        self.room_clients = {}

        # Dados do client
        self.id = None
        self.state = None
        self.score = 0

        # Estado do jogo
        self.name = 'Player'

        self.draw_theme = None
        self.draw_object = None

        # Contexto de execução, armazena informações de execução de cada thread
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((socket.gethostbyname(address), int(port)))

        self.mutex = threading.Lock()
        self.msgs = { '': [] }
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

        # Caso os argumentos sejam vazios, transforma em uma lista vazia
        #
        # NOTA: isso é necessário para evitar que o split gere uma lista com
        # um elemento vazio caso a mensagem não tenha argumentos
        if len(args) == 1 and args[0] == '':
            args = []

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
            if len(args) > 0:
                return 'Número de argumentos inválido'
            return self.name

        elif msg_type == 'CHAT':
            if self.room_clients.get(dest) is None:
                return None

            with self.mutex:
                self.room_clients[dest]['msgs'].append(args[0])

            # Chama o método de tratamento de mensagens de chat a nível de interface
            self.handle_chat(self.room_clients[dest], args[0])

        elif msg_type == 'GUESS':
            if len(args) != 1:
                return 'Número de argumentos inválido'
            elif self.state != 'draw':
                return 'Não estou desenhando'
            elif self.room_clients.get(dest) is None:
                return 'Cliente não encontrado na partida'
            elif self.room_clients[dest]['state'] == 'guess':
                return 'Cliente já acertou o objeto'
            elif self.room_clients[dest]['state'] == 'skip':
                return 'Pulou a rodada, não pode mais dar palpites'
            elif self.room_clients[dest]['state'] == 'draw':
                return 'Não pode dar palpite quando é sua vez de desenhar'

            if args[0] == self.draw_object:
                self.client_got_the_right_answer(dest)

                self.room_clients[dest]['state'] = 'guess'
                self.room_clients[dest]['score'] += 5

                return 'OK'
            return 'Palpite está incorreto'

        elif msg_type == 'GTRA':
            if len(args) != 1:
                return 'Número de argumentos inválido'
            elif self.room_clients.get(args[0]) is None:
                return 'Cliente não encontrado'
            elif self.room_clients[args[0]]['state'] == 'guess':
                return 'Cliente já acertou o objeto'
            elif self.room_clients[args[0]]['state'] == 'draw':
                return 'Quando se esta desenhando não pode dar palpite'
            elif self.room_clients[dest]['state'] == 'skip':
                return 'Pulou a rodada, impossível ter acertado o objeto'

            self.room_clients[args[0]]['state'] = 'guess'
            self.room_clients[args[0]]['score'] += 5
            return 'OK'

        elif msg_type == 'SKIP':
            if len(args) > 0:
                return 'Número de argumentos inválido'
            elif self.room_clients.get(dest) is None:
                return 'Cliente não encontrado'
            elif self.room_clients[dest]['state'] == 'guess':
                return 'Cliente já acertou o objeto'
            elif self.room_clients[dest]['state'] == 'skip':
                return 'A roda já foi pulada'
            elif self.room_clients[dest]['state'] == 'draw':
                return 'Quando se esta desenhando não pode pular a rodada'

            self.room_clients[dest]['state'] = 'skip'
            return 'OK'

        elif msg_type == 'DRAW':
            if len(args) != 1:
                return 'Número de argumentos inválido'
            elif args[0] == self.id:
                self.state = 'draw'

                # Chama o método de tratamento de desenho a nível de interface
                self.handle_draw()

                return 'OK'
            elif self.room_clients.get(args[0]) is None:
                return 'Cliente não encontrado'
            elif self.room_clients[args[0]]['state'] == 'draw':
                return 'Cliente já está desenhando'

            self.room_clients[args[0]]['state'] = 'draw'
            return 'OK'

        elif msg_type == 'FDRAW':
            if len(args) != 1:
                return 'Número de argumentos inválido'

            # Redefine o estado de todos os clientes
            for client in self.room_clients.keys():
                # Calcula a pontuação do cliente que estava desenhando
                if self.room_clients[client]['state'] == 'draw':
                    if args[0] == 'all-guess':  # todos acertaram o objeto
                        self.room_clients[client]['score'] += 8
                    elif args[0] == 'guess':  # ao menos um acertou o objeto
                        self.room_clients[client]['score'] += 5
                    else:  # tempo esgotado
                        self.room_clients[client]['score'] += 2

                self.room_clients[client]['state'] = None

            # Redefine o próprio estado
            self.state = None

            # Atualiza a própria pontuação
            self.score = self.client_score()

            return 'OK'

        elif msg_type == 'CANVAS':
            # Decodifica a imagem e envia para o método de tratamento
            canvas_data = base64.b64decode(args[0])
            canvas_data = zlib.decompress(canvas_data)
            canvas_data = json.loads(canvas_data.decode('utf-8'))

            # Chama o método de tratamento da imagem a nível de interface
            self.handle_canvas(canvas_data)

        elif msg_type == 'SCORE':
            if len(args) > 0:
                return 'Número de argumentos inválido'
            elif self.room_clients.get(dest) is None:
                return 'Cliente não encontrado'

            return self.room_clients[dest]['score']

        return None

    @abc.abstractmethod
    def handle_chat(self, client, message):
        '''
        Função que deve ser implementada pela interface para que ela possa
        manipular as mensagens de chat que chegarem.
        '''
        raise NotImplementedError('handle_chat must be implemented')

    @abc.abstractmethod
    def handle_draw(self):
        '''
        Função que deve ser implementada também pela interface para que possa
        seguir com o processo de iniciar o desenho: escolher uma palavra,
        limpar a tela de desenho atual, etc.
        '''
        raise NotImplementedError('handle_draw must be implemented')

    @abc.abstractmethod
    def handle_canvas(self, canvas):
        '''
        Essa função é chamada no momento que a interface precisa sincronizar
        seus canvas, por exemplo, o cliente que está desenhando envia o
        desenha para que o outro cliente possa visualizá-lo é essa função que
        faz o trabalho de mostrar os dados na tela.
        '''
        raise NotImplementedError('handle_canvas must be implemented')


    ###
    ### Métodos principais para comunicação
    ###
    def get_message(self, dest):
        '''
        Método que retorna a primeira mensagem da pilha de mensagens do cliente.
        Caso não haja mensagens, ele fica em espera até que uma nova mensagem
        chegue.
        '''
        while True:
            with self.mutex:
                if len(self.msgs[dest]) == 0:
                    continue

                return self.msgs[dest].pop(0)

    def send_message(self, type, *args, dest='', wait_response=True):
        '''
        Método que envia uma mensagem para o servidor ou para outro cliente.
        '''
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
            self.id = res.split('&')[1]
            return True

        self.error = res
        return False

    def server_unregister(self):
        res = self.send_message('UNREGISTER')
        if res == 'OK':
            return True

        self.error = res
        return False

    def server_create_room(self, room_type, room_name, room_theme, room_password=None):
        args = [room_type, room_name, room_theme]
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
            self.room_clients = {}
            return True

        self.error = res
        return False


    ###
    ### Métodos de comunicação com outros clientes
    ###
    def client_chat(self, message):
        with self.mutex:
            for client in self.room_clients.keys():
                self.send_message('CHAT', message, dest=client, wait_response=False)

    def client_guess(self, guess):
        with self.mutex:
            for client_id, client in self.room_clients.items():
                if client['state'] == 'draw':
                    response = self.send_message('GUESS', guess, dest=client_id)

                    if response == 'OK':
                        self.state = 'guess'
                        return True

                    self.error = response
                    return False
        return False

    def client_draw(self, client):
        with self.mutex:
            for room_client in self.room_clients.keys():
                self.send_message('DRAW', client, dest=room_client, wait_response=False)

    def client_finish_draw(self, reason):
        with self.mutex:
            for client in self.room_clients.keys():
                self.send_message('FDRAW', reason, dest=client, wait_response=False)

    def client_skip(self):
        with self.mutex:
            for client in self.room_clients.keys():
                self.send_message('SKIP', dest=client, wait_response=False)

    def client_got_the_right_answer(self, client):
        with self.mutex:
            for room_client in self.room_clients.keys():
                if client == room_client:
                    continue

                self.send_message('GTRA', client, dest=room_client, wait_response=False)

    def client_canvas(self, canvas_data):
        # Comprime a imagem e envia para todos os clientes
        canvas_data = json.dumps(canvas_data).encode('utf-8')
        canvas_data = zlib.compress(canvas_data)
        canvas_data = base64.b64encode(canvas_data).decode()

        with self.mutex:
            for client in self.room_clients.keys():
                self.send_message('CANVAS', canvas_data, dest=client, wait_response=False)

    def client_score(self):
        scores = []
        with self.mutex:
            for client in self.room_clients.keys():
                response = self.send_message('SCORE', dest=client)

                if response is not None and response.isdigit():
                    scores.append(int(response))

        freq = {}
        for score in scores:
            freq[score] = freq.get(score, 0) + 1

        return max(freq, key=lambda x: freq[x])

