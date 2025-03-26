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

        self.client_host = None

        # Contexto de execução, armazena informações de execução de cada thread
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((socket.gethostbyname(address), int(port)))

        self.mutex = threading.Lock()
        self.msgs = {
            '': [],
        }

        self.server_error = None

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
            print('Recebido:', msg)

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
        if len(args) == 1 and args[0] == '':
            args = []


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
                self.send_message('RESP', response, dest=dest)

    def parse_server_message(self, msg_type, args):
        if msg_type == 'CONNECT':
            with self.mutex:
                self.msgs[args[0]] = []

            self.room_clients[args[0]] = {
                'name': self.send_message('GREET', dest=args[0]),
                'msgs': [],
            }

        elif msg_type == 'DISCONNECT':
            with self.mutex:
                del self.msgs[args[0]]

            del self.room_clients[args[0]]
        elif msg_type == 'PLAY':
            self.client_host = (args[0], int(args[1]))

        return None

    def parse_client_message(self, dest, msg_type, args):
        if msg_type == 'GREET':
            return self.name

        elif msg_type == 'CHAT':
            with self.mutex:
                self.room_clients[dest]['msgs'].append(args[0])

            self.handle_chat(self.room_clients[dest], args[0])

        elif msg_type == 'GUESS':
            pass

        elif msg_type == 'GTRA':
            pass

        elif msg_type == 'SKIP':
            pass

        elif msg_type == 'DRAW':
            pass

        elif msg_type == 'FDRAW':
            pass

        elif msg_type == 'CANVAS':
            # Decodifica a imagem e envia para o método de tratamento
            canvas_data = base64.b64decode(args[0])
            canvas_data = zlib.decompress(canvas_data)
            self.handle_canvas(canvas_data)

        return None

    @abc.abstractmethod
    def handle_chat(self, client, message):
        raise NotImplementedError('handle_chat must be implemented')

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
        error = self.server_error
        self.server_error = None

        return error


    ###
    ### Métodos de comunicação com o servidor
    ###
    def server_register(self):
        res = self.send_message('REGISTER', self.name)
        if res == 'OK':
            return True

        self.server_error = res
        return False

    def server_unregister(self):
        res = self.send_message('UNREGISTER')
        if res == 'OK':
            return True

        self.server_error = res
        return False

    def server_create_room(self, room_type, room_name, room_password=None):
        args = [room_type, room_name]
        if room_password is not None:
            args.append(room_password)

        res = self.send_message('ROOM', *args)

        if res is not None and res.isdigit():
            self.room = res
            return True

        self.server_error = res
        return False

    def server_close_room(self):
        res = self.send_message('CROOM')
        if res == 'OK':
            self.room = None
            return True

        self.server_error = res
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

        self.server_error = res
        return False

    def server_status_room(self):
        return self.send_message('STATUS')

    def server_leave_room(self):
        res = self.send_message('LEAVE')
        if res == 'OK':
            self.room = None
            self.room_clients = {}
            return True

        self.server_error = res
        return False


    ###
    ### Métodos de comunicação com outros clientes
    ###
    def client_chat(self, message):
        # TODO: Implementar o envio de mensagem para outros clientes
        ...

    def client_guess(self, guess):
        ...

    def client_draw(self):
        ...

    def client_finish_draw(self):
        ...

    def client_skip(self):
        ...

    def client_got_the_right_answer(self):
        # TODO: Implementar o envio de mensagem para outros clientes informando
        # que o cliente que acertou a palavra
        ...

    def client_canvas(self, canvas_data):
        # Comprime a imagem e envia para todos os clientes
        canvas_data = zlib.compress(canvas_data)
        canvas_data = base64.b64encode(canvas_data).decode()

        # TODO: Implementar o envio do canvas para todos os clientes
        ...
