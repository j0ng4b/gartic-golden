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
        #   'theme': 'room theme',
        #   'state': 'room state',
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

            # Parse message
            msg = msg.decode()
            if '/' not in msg or ':' not in msg:
                self.send_message(address, 'RESP', f'Mensagem inválida: {msg}')
                continue

            threading.Thread(
                target=self.parse_message,
                args=(msg, address)
            ).start()

    def parse_message(self, msg, address):
        dest, msg = msg.split('/')
        msg_type, args = msg.split(':')
        args = args.split(';')
        if len(args) == 1 and args[0] == '':
            args = []

        # Verifica se a mensagem é para o servidor
        if dest == '':
            response = self.parse_server_message(msg_type, args, address)
            self.send_message(address, 'RESP', f'{response}')
            return

        # Repassa a mensagens para o cliente destino
        response = self.routes_client_message(dest, msg_type, args, address)
        if response is not None:
            self.send_message(address, 'RESP', response)


    def parse_server_message(self, msg_type, args, address):
        if msg_type == 'REGISTER':
            if len(args) != 1:
                return 'Número de argumentos inválido'
            elif args[0] == '':
                return 'Nome de jogador inválido'

            self.clients.append({
                'id': str(uuid.uuid4()),
                'name': args[0],
                'room': None,

                'address': address[0],
                'port': address[1],
            })
            return f'OK&{self.clients[-1]["id"]}'

        elif msg_type == 'UNREGISTER':
            if len(args) != 0:
                return 'Número de argumentos inválido'

            client = self.get_client(address[0], address[1])
            if client is None:
                return 'Cliente não registrado'

            self.clients.remove(client)
            return 'OK'

        elif msg_type == 'ROOM':
            if len(args) < 3 or len(args) > 4:
                return 'Número de argumentos inválido'
            elif args[0] not in ['priv', 'pub']:
                return 'Tipo da sala inválido'
            elif args[1] == '':
                return 'Nome da sala inválido'
            elif args[0] == 'priv' and len(args) != 4:
                return 'Senha não fornecida para sala privada'
            elif args[0] == 'pub' and len(args) != 3:
                return 'Sala pública não requer senha'

            client = self.get_client(address[0], address[1])
            if client is None:
                return 'Cliente não registrado'

            if client['room'] is not None:
                return 'Cliente já está em uma sala'

            # A lista de clientes da sala recém-criada neste momento possui apenas o host da sala.
            # O código da sala será sempre a quantidade de salas existentes mais 1.
            code = str(len(self.rooms) + 1)
            self.rooms.append({
                'name': args[1],
                'code': code,
                'state': 'lobby',
                'theme': args[2],
                'password': args[3] if len(args) == 4 else None,
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

            if len(room['clients']) == 1:
                return 'Poucos clientes na sala'

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
                if (len(args) == 1 and room_type != args[0]) or room['state'] != 'lobby':
                    continue

                res += f"{room_type},{room['name']},{room['code']},{room['theme']},"
                res += f"{str(len(room['clients']))},{room['max_clients']}\n"

            return res

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
            client['room'] = None

            # Remove o cliente que deseja sair da lista de clientes daquela sala
            room['clients'].remove((client['id'], address[0], address[1]))
            if len(room['clients']) == 0:
                # Se não houver mais nenhum cliente na sala, apagar a sala
                self.rooms.remove(room)
            else:
                # Se houver clientes na sala notifica a eles que o cliente atual saiu
                for address in room['clients']:
                    address = (address[1], address[2])
                    self.send_message(address, 'DISCONNECT', client['id'])

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

            if room['state'] != 'lobby':
                return 'A sala não está disponível'

            # Verifica se o cliente está na sala
            if client['room'] is not None:
                if client['room'] == args[0]:
                    return 'Cliente já está na sala'
                return 'Cliente já está em outra sala'

            # Verifica a senha da sala
            if room['password'] is not None and len(args) != 2:
                return 'Senha não fornecida'
            elif room['password'] is not None and args[1] != room['password']:
                return 'Senha da sala está incorreta'

            # Adiciona o cliente na sala
            client['room'] = room['code']
            room['clients'].append((client['id'], address[0], address[1]))

            # Notifica os clientes da sala que um novo cliente entrou
            for room_client in room['clients']:
                if room_client[0] == client['id']:
                    continue

                # Envia uma mensagem para o cliente que está na sala para se
                # conectar com o novo cliente
                room_client_address = (room_client[1], room_client[2])
                self.send_message(room_client_address, 'CONNECT', client['id'])

                # Envia uma mensagem para o cliente que está entrando para se
                # conectar com o cliente que já está na sala
                self.send_message(address, 'CONNECT', room_client[0])

            if len(room['clients']) == room['max_clients']:
                self.close_room(room)

            return 'OK'

        elif msg_type == 'END':
            if len(args) != 0:
                return 'Número de argumentos inválido'

            client = self.get_client(address[0], address[1])
            if client is None:
                return 'Cliente não registrado'

            room_code = client['room']
            room = self.get_room(room_code)
            if room_code == '' or room is None:
                return 'Cliente não está em nenhuma sala'

            if room['clients'][0][0] != client['id']:
                return 'Somente o dono da sala pode excluí-la'

            if room['state'] != 'game':
                return 'A sala não está em partida'

            for room_client in room['clients']:
                if room_client[0] == client['id']:
                    continue
                self.send_message((room_client[1], room_client[2]), 'END')

            self.rooms.remove(room)
            return 'OK'

        return 'Tipo de mensagem inválido'

    def routes_client_message(self, dest, msg_type, args, address):
        client = self.get_client(address[0], address[1])
        if client is None:
            return 'Cliente não registrado'

        if client['id'] == dest:
            return 'Cliente destino é o próprio cliente'

        room = self.get_room(client['room'])
        if room is None:
            return 'Cliente não está em nenhuma sala'

        msg = f'{client["id"]}/{msg_type}:{";".join(args)}'.encode()
        for room_client in room['clients']:
            if room_client[0] == dest:
                self.socket.sendto(msg, (room_client[1], room_client[2]))
                return None

        return 'Cliente destino não encontrado'

    def send_message(self, address, type, *args):
        self.socket.sendto(f"/{type}:{';'.join(args)}".encode(), address)

    def close_room(self, room):
        for client in room['clients']:
            if client == room['clients'][0]:
                continue

            self.send_message((client[1], client[2]), 'PLAY')

        # Notifica o cliente dono da sala que pode iniciar o jogo
        address = (room['clients'][0][1], room['clients'][0][2])
        self.send_message(address, 'GAME')
        room['state'] = 'game'

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
