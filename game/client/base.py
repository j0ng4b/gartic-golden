import logging
import socket
import threading


class BaseClient:
    def __init__(self, address, port):
        if self.__class__ is BaseClient:
            raise TypeError("BaseClient class cannot be instantiated")


        if address is None or port is None:
            raise ValueError('server address and port must be set')

        self.name = 'Player'

        self.room = None

        # Contexto de execução, armazena informações de execução de cada thread
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.connect((address, int(port)))

        self.context = {
            # Contexto de execução da padrão
            0: {
                'socket': server_socket,
                'mutex': threading.Lock(),
                'msgs': [],
            }
        }

    def start(self):
        # Inicia o a comunicação com o servidor, deve ser inciado antes de
        # qualquer coisa devido a pilha de mensagem
        server_thrd = threading.Thread(target=self.handle_messages, args=(self.parse_server_message,))
        server_thrd.daemon = True
        server_thrd.start()

        self.server_register()

    def handle_messages(self, parser):
        while True:
            # Quando não acha o contexto para a thread usa o contexto padrão, ou
            # seja, essa é a thread de comunicação com o servidor
            context = self.get_context()

            # Essa função recebe toda e qualquer mensagem mesmo as que não são
            # comandos do servidor
            msg = context['socket'].recv(1024).decode()

            # Quando há um ':' na message essa é uma mensagem de comando vinda
            # do servidor, faz análise da mensagem
            if ':' in msg:
                msg_type, args = msg.split(':')
                args = args.split(';')
                if len(args) == 1 and args[0] == '':
                    args = []

                response = parser(msg_type, args)
                if response is not None:
                    context['socket'].sendall(response.encode())

                continue

            # Quando não é um comando do servidor apenas joga a mensagem na
            # pilha de mensagens para que seja analisada por outra parte do
            # código
            with context['mutex']:
                context['msgs'].append(msg)

    def setup_client(self, address, port):
        thread_id = threading.current_thread().ident
        if thread_id is None:
            raise Exception('No thread identifier')

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.connect((address, int(port)))

        # Armazena informações do cliente conectados a sala
        self.context[thread_id] = {
            'socket': client_socket,
            'mutex': threading.Lock(),
            'msgs': [],

            'name': None,
        }

        self.handle_messages(self.parser_client_message)

    def parse_server_message(self, msg_type, args):
        if msg_type == 'CONNECT':
            client_thread = threading.Thread(target=self.setup_client, args=args)
            client_thread.daemon = True
            client_thread.start()
        return None

    def parser_client_message(self, msg_type, args):
        return None


    ###
    ### Métodos principais para comunicação
    ###
    def get_context(self):
        context_id = threading.current_thread().ident
        if context_id is None:
            return self.context[0]

        context = self.context.get(context_id)
        if context is None:
            context = self.context[0]

        return context

    def get_message(self):
        context = self.get_context()

        while True:
            with context['mutex']:
                if len(context['msgs']) == 0:
                    continue

                return context['msgs'].pop(0)

    def send_message(self, type, *args):
        context = self.get_context()

        context['socket'].send(f"{type}:{';'.join(args)}".encode())
        return self.get_message()


    ###
    ### Métodos de comunicação com o servidor
    ###
    def server_register(self):
        res = self.send_message('REGISTER', self.name)
        return res == 'OK'

    def server_create_room(self, room_type, room_name, room_password=None):
        args = [room_type, room_name]
        if room_password is not None:
            args.append(room_password)

        res = self.send_message('ROOM', *args)

        if res.isdigit():
            self.room = res
            return True

        return False

    def server_close_room(self, room_code):
        ...

    def server_list_rooms(self, room_type=None):
        args = []
        if room_type is not None:
            args.append(room_type)

        res = self.send_message('LIST', *args)

        rooms = None
        if res.find('\n'):
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

        return False

    def server_status_room(self):
        res = self.send_message('STATUS')
        logging.warning(f'{res}')

