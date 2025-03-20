import socket


class Server:
    def __init__(self, address, port):
        if address is None or port is None:
            raise ValueError('server address and port must be set')

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((address, int(port)))


        # Store the list rooms on below format
        #
        # Room
        # {
        #   'name': 'room name',
        #   'code': 'room code',
        #   'max_clients': number maximum clients,
        #   'clients': [
        #     Client,
        #   ]
        # }
        #
        # Client
        # [
        #   'address',
        #   port
        # ]
        self.rooms = []

        # Store the list of client on below format
        #
        # Client
        # {
        #   'name': 'client name',
        #   'room': 'room code',
        #
        #   'address': 'address of the client',
        #   'port': port number of the client
        # }
        self.clients = []


    def start(self):
        while True:
            msg, address = self.socket.recvfrom(1024)

            # Parse message
            msg_type, args = msg.decode().split(':')
            args = args.split(';')
            response = self.parse_message(msg_type, args, address)

            # Sends response to client
            self.socket.sendto(response.encode(), address)


    def parse_message(self, msg_type, args, address):
        if msg_type == 'REGISTER':
            if len(args) != 1:
                return 'Número de argumentos inválido'
            elif args[0] == '':
                return 'Nome de jogador inválido'

            self.clients.append({
                'name': args[0],
                'room': '',

                'address': address[0],
                'port': address[1],
            })
        elif msg_type == 'ROOM':
            if len(args) < 2 or len(args) > 3:
                return 'Número de argumentos inválido'
            elif args[0] != 'priv' or args[0] != 'pub':
                return 'Tipo da sala inválido'
            elif args[1] == '':
                return 'Nome da sala inválido'
            elif args[0] == 'priv' and len(args) == 2:
                return 'Senha não fornecida para sala privada'
            elif args[0] == 'pub' and len(args) == 3:
                return 'Sala pública não requer senha'

            # TODO: implement success action
        elif 'CROOM':
            # TODO: implement fail condition
            # TODO: implement success action
            pass

        elif 'LIST':
            if len(args) == 1 and (args[0] != 'priv' or args[0] != 'pub'):
                return 'Tipo da sala inválido'

            # TODO: implement success action

        elif 'ENTER':
            # TODO: implement fail condition
            # TODO: implement success action
            pass

        return 'OK'

