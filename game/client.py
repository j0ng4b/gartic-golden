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

        # Start the server thread
        server_thrd = threading.Thread(target=self.handle_server_messages)
        server_thrd.daemon = True
        server_thrd.start()

        while True:
            # TODO: client logic
            ...

    def handle_input(self):
        ...

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
        args = [room_type, room_name]
        if room_password is not None:
            args.append(room_password)

        res = self.send_message('ROOM', *args)

        # Se for possível converter res em um inteiro quer dizer que a sala foi criada com sucesso.
        if res.isdigit():
            logging.warning(f'Sala criada com sucesso, código: {res}')
        else:
            logging.warning(f'Sala não criada, motivo: {res}')

    def close_room(self, room_code):
        ...

    def list_rooms(self, room_type=None):
        args = []
        if room_type is not None:
            args.append(room_type)

        res = self.send_message('LIST', *args)
        logging.warning(f'{res}')

    def enter_room(self, room_code, room_password=None):
        args = [room_code]
        if room_password is not None:
            args.append(room_password)

        res = self.send_message('ENTER', *args)
        if res != 'OK':
            logging.error(res)

