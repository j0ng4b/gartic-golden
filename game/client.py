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

        self.name = 'Player'

        self.room = None

    def start(self):
        self.register()

        # Start the server thread
        server_thrd = threading.Thread(target=self.handle_server_messages)
        server_thrd.daemon = True
        server_thrd.start()

    def handle_server_messages(self):
        while True:
            msg = self.socket.recv(1024).decode()

            # Parse message
            if ':' not in msg:
                logging.error('Mensagem inválida')
                continue

            msg_type, args = msg.split(':')
            args = args.split(';')
            if len(args) == 1 and args[0] == '':
                args = []

            response = self.parse_message(msg_type, args)
            if response is not None:
                self.socket.sendall(response.encode())


    def parse_message(self, msg_type, args, address=None):
        return 'Tipo de mensagem inválido'

    ###
    ### Sever communication methods
    ###
    def send_message(self, type, *args):
        self.socket.sendall(f'{type}:{';'.join(args)}'.encode())
        return self.socket.recv(1034).decode()

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

