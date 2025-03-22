import logging
import socket
import threading


class BaseClient:
    def __init__(self, address, port):
        if self.__class__ is BaseClient:
            raise TypeError("BaseClient class cannot be instantiated")


        if address is None or port is None:
            raise ValueError('server address and port must be set')

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((address, int(port)))

        self.mutex = threading.Lock()
        self.msgs = []

        self.name = 'Player'

        self.room = None

    def start(self):
        # Inicia o a comunicação com o servidor, deve ser inciado antes de
        # qualquer coisa devido a pilha de mensagem
        server_thrd = threading.Thread(target=self.handle_server_messages)
        server_thrd.daemon = True
        server_thrd.start()

        self.register()

    def handle_server_messages(self):
        while True:
            # Essa função recebe toda e qualquer mensagem mesmo as que não são
            # comandos do servidor
            msg = self.socket.recv(1024).decode()

            # Quando há um ':' na message essa é uma mensagem de comando vinda
            # do servidor, faz análise da mensagem
            if ':' in msg:
                msg_type, args = msg.split(':')
                args = args.split(';')
                if len(args) == 1 and args[0] == '':
                    args = []

                response = self.parse_message(msg_type, args)
                if response is not None:
                    self.socket.sendall(response.encode())

                continue

            # Quando não é um comando do servidor apenas joga a mensagem na
            # pilha de mensagens para que seja analisada por outra parte do
            # código
            with self.mutex:
                self.msgs.append(msg)


    def parse_message(self, msg_type, args, address=None):
        return None

    ###
    ### Métodos de comunicação com o servidor
    ###
    def get_message(self):
        while True:
            with self.mutex:
                if len(self.msgs) == 0:
                    continue

                return self.msgs.pop(0)

    def send_message(self, type, *args):
        self.socket.sendall(f"{type}:{';'.join(args)}".encode())
        return self.get_message()

    def register(self):
        res = self.send_message('REGISTER', self.name)
        return res == 'OK'

    def create_room(self, room_type, room_name, room_password=None):
        args = [room_type, room_name]
        if room_password is not None:
            args.append(room_password)

        res = self.send_message('ROOM', *args)

        if res.isdigit():
            self.room = res
            return True

        return False

    def close_room(self, room_code):
        ...

    def list_rooms(self, room_type=None):
        args = []
        if room_type is not None:
            args.append(room_type)

        res = self.send_message('LIST', *args)

        rooms = None
        if res.find('\n'):
            rooms = res.split('\n')

        return rooms

    def enter_room(self, room_code, room_password=None):
        args = [room_code]
        if room_password is not None:
            args.append(room_password)

        res = self.send_message('ENTER', *args)
        if res == 'OK':
            self.room = room_code
            return True

        return False

    def status_room(self):
        res = self.send_message('STATUS')
        logging.warning(f'{res}')

