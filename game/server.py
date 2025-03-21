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
        #   'password': 'room password',
        #   'max_clients': number maximum clients,
        #   'clients': [
        #     Client,
        #   ]
        # }
        #
        # Client
        # (
        #   'address',
        #    port
        # )
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
            print('\nCriando Sala')
            if len(args) != 4:
                return 'Número de argumentos inválido'
            elif args[0] not in ['priv', 'pub']:
                return 'Tipo da sala inválido'
            elif args[1] == '':
                return 'Nome da sala inválido'
            elif args[0] == 'priv' and args[3] == 'No':
                return 'Senha não fornecida para sala privada'
            elif args[0] == 'pub' and args[3] != 'No':
                return 'Sala pública não requer senha'

            # A lista de clientes da sala recém-criada neste momento possui apenas o host da sala.
            # O código da sala será sempre a quantidade de salas existentes mais 1.
            code = str(len(self.rooms) + 1)
            self.rooms.append({
                'name': args[1],
                'code': code,
                'password': args[3],
                'max_clients': args[2],
                'clients': [
                    (address[0], address[1]),
                ]
            })

            return code

        elif msg_type == 'CROOM':
            # TODO: implement fail condition
            # TODO: implement success action
            pass

        elif msg_type == 'LIST':
            if args[0] not in ['priv', 'pub']:
                return 'Tipo da sala inválido'

            contents = []
            type_room = ''
            if args[0] == 'priv':
                contents = list(
                    filter(lambda room: room['password'] != 'No', self.rooms))
                type_room = 'priv'
            else:
                contents = list(
                    filter(lambda room: room['password'] == 'No', self.rooms))
                type_room = 'pub'

            if contents == []:
                return 'Nenhuma sala encontrada'

            res = ''
            for content in contents:
                clients_current = str(len(content['clients']))
                res += type_room + ',' + content['name'] + ',' + content['code'] + \
                    ',' + clients_current + ',' + content['max_clients'] + '\n'

            return res

        elif msg_type == 'ENTER':
            # TODO: implement fail condition
            # TODO: implement success action
            pass

        return 'OK'
