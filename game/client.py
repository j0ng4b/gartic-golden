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


class TextClient(BaseClient):
    def __init__(self, address, port):
        super().__init__(address, port)

        self.menu = 0

    def start(self):
        super().start()

        while True:
            if self.menu == 0:
                self.main_menu()
            elif self.menu == 1:
                self.create_room_menu()
            elif self.menu == 2:
                self.list_rooms_menu()
            elif self.menu == 3:
                self.enter_room_menu()

    def main_menu(self):
        print('Opções:')
        print('1. Criar sala')
        print('2. Listar sala')
        print('3. Entrar em uma sala')
        opt = input('> ')

        if not opt.isdigit():
            print('=== opção inválida ===')
            return

        opt = int(opt)
        if opt < 1 and opt > 3:
            print('=== opção inválida ===')
            return
        else:
            self.menu = opt
            return

    def create_room_menu(self):
        print('Criação de sala:')
        print('1. pública')
        print('2. privada')
        print('0. cancelar')
        opt = input('> ')

        if not opt.isdigit():
            print('=== opção inválida ===')
            return

        opt = int(opt)
        ok = False

        if opt < 0 and opt > 2:
            print('=== opção inválida ===')
            return

        elif opt == 0:
            self.menu = 0
            return

        elif opt == 1:
            name = input('Nome da sala: ')
            ok = self.create_room('pub', name)

        elif opt == 2:
            name = input('Nome da sala: ')
            password = input('Senha da sala: ')
            ok = self.create_room('priv', name, password)

        if ok:
            print(f'Código da sala criada: {self.room}')
        else:
            print('Não foi possível criar a sala')

    def list_rooms_menu(self):
        print('Listar salas:')
        print('1. todas')
        print('2. públicas')
        print('3. privadas')
        print('0. cancelar')
        opt = input('> ')

        if not opt.isdigit():
            print('=== opção inválida ===')
            return

        opt = int(opt)
        rooms = None

        if opt < 0 and opt > 3:
            print('=== opção inválida ===')
            return

        elif opt == 0:
            self.menu = 0
            return

        elif opt == 1:
            rooms = self.list_rooms()

        elif opt == 2:
            rooms = self.list_rooms('pub')

        elif opt == 3:
            rooms = self.list_rooms('priv')

        if rooms is None:
            print('Não há salas')
            return

        for room in rooms:
            print(room)

    def enter_room_menu(self):
        # TODO: implementar entrar na sala
        self.menu = 0
