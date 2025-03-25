import socket
import threading
import uuid


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
        #   'id',
        #   'address',
        #    port
        # )
        self.rooms = []

        # Store the list of client on below format
        #
        # Client
        # {
        #   'id': 'client id',
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
            print(f'Mensagem {msg} recebida de {address}')

            # Parse message
            msg = msg.decode()
            if ':' not in msg:
                self.socket.sendto(f'Mensagem inválida: {msg}'.encode(), address)
                continue

            threading.Thread(
                target=self.parse_message,
                args=(msg, address)
            ).start()

    def parse_message(self, msg, address):
        msg_type, args = msg.split(':')
        args = args.split(';')
        if len(args) == 1 and args[0] == '':
            args = []


        # Processa e responde mensagens direcionadas ao servidor
        response = self.parse_server_message(msg_type, args, address)
        if response is not None:
            self.socket.sendto(response.encode(), address)
            return


        # Repassa mensagens direcionadas a outros clientes
        client = self.get_client(address[0], address[1])
        if client is not None:
            room = self.get_room(client['room'])
            if room is not None:
                for client in room['clients']:
                    if client == address:
                        continue

                    self.socket.sendto(msg.encode(), client)


    def parse_server_message(self, msg_type, args, address):
        if msg_type == 'REGISTER':
            if len(args) != 1:
                return 'Número de argumentos inválido'
            elif args[0] == '':
                return 'Nome de jogador inválido'

            self.clients.append({
                'id': str(uuid.uuid4()),
                'name': args[0],
                'room': '',

                'address': address[0],
                'port': address[1],
            })
            return 'OK'

        elif msg_type == 'UNREGISTER':
            if len(args) != 0:
                return 'Número de argumentos inválido'

            client = self.get_client(address[0], address[1])
            if client is None:
                return 'Cliente não registrado'

            self.clients.remove(client)
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

            if client['room'] != '':
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
                    (client['id'], client['address'], client['port']),
                ]
            })

            # Associa o cliente com a sala criada
            client['room'] = code
            return code

        elif msg_type == 'CROOM':
            if len(args) != 0:
                return 'Número de argumentos inválido'

            client = self.get_client(address[0], address[1])
            if client is None:
                return 'Cliente não registrado'

            room = self.get_room(client['room'])
            if client['room'] == '' or room is None:
                return 'Cliente não está em nenhuma sala'

            if room['clients'][0][0] != client['id']:
                return 'Somente o dono da sala pode fechá-la'

            self.close_room(room)
            return 'OK'

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
            if len(args) != 0:
                return 'Número de argumentos inválido'

            client = self.get_client(address[0], address[1])
            if client is None:
                return 'Cliente não registrado'

            room_code = client['room']
            room = self.get_room(room_code)
            if room_code == '' or room is None:
                return 'Cliente não está em nenhuma sala'

            room_type = 'priv' if room['password'] is not None else 'pub'
            return f"{room_type},{room['name']},{room['code']},{str(len(room['clients']))},{room['max_clients']}"

        elif msg_type == 'LEAVE':
            if len(args) != 0:
                return 'Número de argumentos inválido'

            client = self.get_client(address[0], address[1])
            if client is None:
                return 'Cliente não registrado'

            room_code = client['room']
            room = self.get_room(room_code)
            if room_code == '' or room is None:
                return 'Cliente não está em nenhuma sala'

            # Retira o código da sala do cliente registrado
            client['room'] = ''

            # Remove o cliente que deseja sair da lista de clientes daquela sala
            room['clients'].remove((address[0], address[1]))
            if len(room['clients']) == 0:
                # Se não houver mais nenhum cliente na sala, apagar a sala
                self.rooms.remove(room)
            else:
                # Se houver clientes na sala notifica a eles que o cliente atual saiu
                msg_leave = f'DISCONNECT:{client["id"]}'
                for address in room['clients']:
                    address = (address[1], address[2])
                    self.socket.sendto(msg_leave.encode(), address)

            return 'OK'

        elif msg_type == 'ENTER':
            client = self.get_client(address[0], address[1])
            if client is None:
                return 'Cliente não registrado'

            if len(args) > 2:
                return 'Número de argumentos inválido'

            # Verifica se a sala existe
            room = self.get_room(args[0])
            if room is None:
                return 'Código da sala inválido'

            # Verifica se o cliente está na sala
            if client['room'] != '':
                if client['room'] == args[0]:
                    return 'Cliente já está na sala'
                return 'Cliente já está em outra sala'

            # Verifica a senha da sala
            if room['password'] is not None and len(args) != 2:
                return 'Senha não fornecida'
            elif room['password'] is not None and args[1] != room['password']:
                return 'Senha da sala está incorreta'

            # Notifica os clientes da sala que um novo cliente entrou
            for room_client in room['clients']:
                room_client_address = (room_client[1], room_client[2])

                # Envia uma mensagem para o cliente que está na sala para se
                # conectar com o novo cliente
                self.socket.sendto(f'CONNECT:{client["id"]}'.encode(), room_client_address)

                # Envia uma mensagem para o cliente que está entrando para se
                # conectar com o cliente que já está na sala
                self.socket.sendto(f'CONNECT:{room_client[0]}'.encode(), address)

            client['room'] = room['code']
            room['clients'].append(address)

            if len(room['clients']) == room['max_clients']:
                self.close_room(room)

            return 'OK'

        return None

    def close_room(self, room):
        for client in room['clients']:
            if client == room['clients'][0]:
                continue

            self.socket.sendto(f'PLAY:'.encode(), client)

        # Notifica o cliente dono da sala que pode iniciar o jogo
        address = (room['clients'][0][1], room['clients'][0][2])
        self.socket.sendto(f'GAME:'.encode(), address)
        self.rooms.remove(room)

    def get_client(self, address, port):
        for client in self.clients:
            if client['address'] == address and client['port'] == port:
                return client

        return None

    def get_room(self, code):
        for room in self.rooms:
            if room['code'] == code:
                return room

        return None

