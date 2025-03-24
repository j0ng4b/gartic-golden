import logging
import socket
import threading


class BaseClient:
    def __init__(self, address, port):
        if self.__class__ is BaseClient:
            raise TypeError("BaseClient class cannot be instantiated")


        if address is None or port is None:
            raise ValueError('server address and port must be set')
        self.address = (socket.gethostbyname(address), int(port))

        self.name = 'Player'

        self.room = None
        self.room_clients = {}

        # Contexto de execução, armazena informações de execução de cada thread
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', 0))

        self.mutex = threading.Lock()
        self.msgs = {
            self.address: [],
        }

    def start(self):
        # Inicia o a comunicação com o servidor, deve ser inciado antes de
        # qualquer coisa devido a pilha de mensagem
        thread = threading.Thread(target=self.handle_messages)
        thread.daemon = True
        thread.start()

        self.server_register()

    def handle_messages(self):
        while True:
            # Essa função recebe toda e qualquer mensagem mesmo as que não são
            # comandos do servidor
            msg, address = self.socket.recvfrom(1024)

            # Quando há um ':' na message essa é uma mensagem de comando vinda
            # do servidor, faz análise da mensagem
            msg = msg.decode()
            if ':' in msg:
                msg_type, args = msg.split(':')
                args = args.split(';')
                if len(args) == 1 and args[0] == '':
                    args = []

                threading.Thread(
                    target=self.parser_message,
                    args=(msg_type, args, address)
                ).start()
                continue

            # Quando não é um comando do servidor apenas joga a mensagem na
            # pilha de mensagens para que seja analisada por outra parte do
            # código
            with self.mutex:
                self.msgs[self.address].append(msg)

    def parser_message(self, msg_type, args, address):
        response = None

        if address == self.address:
            response = self.parse_server_message(msg_type, args)
        else:
            response = self.parse_client_message(msg_type, args)

        if response is not None:
            self.socket.sendto(response.encode(), address)

    def parse_server_message(self, msg_type, args):
        if msg_type == 'CONNECT':
            with self.mutex:
                self.msgs[(args[0], int(args[1]))] = []

            self.room_clients[(args[0], int(args[1]))] = {
                'name': self.send_message('GREET', address=(args[0], int(args[1]))),
                'address': (args[0], int(args[1])),
            }

        return None

    def parse_client_message(self, msg_type, args):
        if msg_type == 'GREET':
            return self.name

        return None


    ###
    ### Métodos principais para comunicação
    ###
    def get_message(self, address):
        while True:
            with self.mutex:
                if len(self.msgs[address]) == 0:
                    continue

                return self.msgs[address].pop(0)

    def send_message(self, type, *args, address=None, wait_response=True):
        if address is None:
            address = self.address

        self.socket.sendto(f"{type}:{';'.join(args)}".encode(), address)

        if not wait_response:
            return None
        return self.get_message(address)


    ###
    ### Métodos de comunicação com o servidor
    ###
    def server_register(self):
        res = self.send_message('REGISTER', self.name)
        return res == 'OK'

    def server_unregister(self):
        res = self.send_message('UNREGISTER', self.name)
        return res == 'OK'

    def server_create_room(self, room_type, room_name, room_password=None):
        args = [room_type, room_name]
        if room_password is not None:
            args.append(room_password)

        res = self.send_message('ROOM', *args)

        if res is not None and res.isdigit():
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

        return False

    def server_status_room(self):
        res = self.send_message('STATUS')
        logging.warning(f'{res}')

    def server_leave_room(self):
        res = self.send_message('LEAVE')
        if res == 'OK':
            self.room = None
            return True

        return False

