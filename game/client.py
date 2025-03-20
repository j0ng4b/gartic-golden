import logging
import socket


class Client:
    def __init__(self, address, port):
        if address is None or port is None:
            raise ValueError('server address and port must be set')

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((address, int(port)))

        self.name = 'Player'

    def start(self):
        self.register()

    def handle_input(self):
        ...


    ###
    ### Communication methods
    ###
    def send_message(self, type, *args):
        self.socket.sendall(f'{type}:{';'.join(args)}'.encode())
        return self.socket.recv(1034).decode()

    def register(self):
        res = self.send_message('REGISTER', self.name)
        if res != 'OK':
            logging.error(res)

    def create_room(self, room_type, room_name, room_password=None):
        ...

    def close_room(self, room_code):
        ...

    def list_rooms(self, room_type=None):
        ...

    def enter_room(self, room_code, room_password=None):
        ...

