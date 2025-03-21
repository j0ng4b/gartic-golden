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
            msg = msg.decode()
            if ':' not in msg:
                self.socket.sendto('Mensagem inválida'.encode(), address)
                continue

            msg_type, args = msg.split(':')
            args = args.split(';')
            if len(args) == 1 and args[0] == '':
                args = []

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

            return 'OK'

        elif msg_type == 'ROOM':
            if len(args) < 2 or len(args) > 3:
                return 'Número de argumentos inválido'
            elif args[0] not in ['priv', 'pub']:
                return 'Tipo da sala inválido'
            elif args[1] == '':
                return 'Nome da sala inválido'
            elif args[0] == 'priv' and len(args) != 3:
                return 'Senha não fornecida para sala privada'
            elif args[0] == 'pub' and len(args) != 2:
                return 'Sala pública não requer senha'

            client = self.get_client(address[0], address[1])
            if client is None:
                return 'Cliente não registrado'

            if self.clients[client]['room'] != '':
                return 'Cliente já está em uma sala'

            # A lista de clientes da sala recém-criada neste momento possui apenas o host da sala.
            # O código da sala será sempre a quantidade de salas existentes mais 1.
            code = str(len(self.rooms) + 1)
            self.rooms.append({
                'name': args[1],
                'code': code,
                'password': args[2] if len(args) == 3 else None,
                'max_clients': 10,  # Por enquanto é um valor fixo
                'clients': [
                    # address é uma tupla, com o primeiro elemento sendo o
                    # endereço IP e o segundo sendo a porta do cliente
                    address,
                ]
            })

            # Associa o cliente com a sala criada
            self.clients[client]['room'] = code
            return code

        elif msg_type == 'CROOM':
            # TODO: implement fail condition
            # TODO: implement success action
            pass

        elif msg_type == 'LIST':
            if len(args) == 1 and args[0] not in ['priv', 'pub']:
                return 'Tipo da sala inválido'
            elif len(args) > 1:
                return 'Número de argumentos inválido'

            res = ''
            for room in self.rooms:
                room_type = 'priv' if room['password'] is not None else 'pub'
                if len(args) == 1 and room_type != args[0]:
                    continue

                res += f"{room_type},{room['name']},{room['code']},"
                res += f"{str(len(room['clients']))},{room['max_clients']}\n"

            return res

        elif msg_type == 'STATUS':
            index_client = self.get_client(address[0], address[1])
            room_code = self.clients[index_client]['room']
            if room_code == '':
                return 'Não possui sala'
            else:
                index_room = self.get_room(room_code)
                room = self.rooms[index_room]
                room_type = 'priv' if room['password'] is not None else 'pub'
                return f"{room_type},{room['name']},{room['code']},{room_code},{str(len(room['clients']))},{room['max_clients']}\n"

        elif msg_type == 'ENTER':
            if len(args) > 2:
                return 'Número de argumentos inválido'

            # Verifica se a sala existe
            room = self.get_room(args[0])
            if room is None:
                return 'Código da sala inválido'

            # Verifica se o cliente está na sala
            for room_client in self.rooms[room]['clients']:
                if room_client == address:
                    return 'Cliente já está na sala'

            # Verifica a senha da sala
            if self.rooms[room]['password'] is not None and len(args) != 2:
                return 'Senha não fornecida'
            elif self.rooms[room]['password'] is not None and args[1] != self.rooms[room]['password']:
                return 'Senha da sala está incorreta'

            # TODO: Notifica os clientes da sala que um novo cliente entrou
            # TODO: Adiciona o cliente na sala

            return 'OK'

        return 'Tipo de mensagem inválido'

    def get_client(self, address, port):
        for i in range(len(self.clients)):
            if self.clients[i]['address'] == address and self.clients[i]['port'] == port:
                return i

        return None

    def get_room(self, code):
        for i in range(len(self.rooms)):
            if self.rooms[i]['code'] == code:
                return i

        return None

