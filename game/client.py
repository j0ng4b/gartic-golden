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
        self.list_rooms('priv')
        self.list_rooms('pub')

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

    def create_room(self, room_type, room_name, max_clients, room_password='No'):
        res = self.send_message('ROOM', room_type, room_name, max_clients, room_password)
        # Se for possível converter res em um inteiro quer dizer que a sala foi criada com sucesso.
        try:
            code = int(res)
            logging.warning(f'Sala criada com sucesso, código: {code}')
        except ValueError as ex:
            logging.warning(f'Sala não criada, motivo: {res}')

    def close_room(self, room_code):
        ...

    def list_rooms(self, room_type):
        res = self.send_message('LIST', room_type)
        logging.warning(f'{res}')

    def enter_room(self, room_code, room_password=None):
        ...

