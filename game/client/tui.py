from game.client.base import BaseClient

class TUIClient(BaseClient):
    def __init__(self, address, port):
        super().__init__(address, port)

        self.menu = 0
        self.rooms = None

    def start(self):
        super().start()

        while True:
            if self.menu == 0:
                if self.room is None:
                    self.main_menu()
                else:
                    self.room_menu()
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
        print('0. Sair')
        opt = input('> ')

        if not opt.isdigit():
            print('=== opção inválida ===')
            return

        opt = int(opt)
        if opt < 0 or opt > 3:
            print('=== opção inválida ===')
            return
        elif opt == 0:
            self.server_unregister()
            exit(0)
        else:
            self.menu = opt
            return

    def room_menu(self):
        print('Opções da sala:')
        print('1. Sair da sala')
        print('2. Enviar mensagem')
        print('3. Fechar sala')
        opt = input('> ')

        if not opt.isdigit():
            print('=== opção inválida ===')
            return

        opt = int(opt)
        if opt < 1 or opt > 3:
            print('=== opção inválida ===')
            return

        if opt == 1:
            self.server_leave_room()
            self.menu = 0
        elif opt == 2:
            message = input('Mensagem: ')
            self.client_chat(message)
        elif opt == 3:
            self.server_close_room()
            self.menu = 0

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

        if opt < 0 or opt > 2:
            print('=== opção inválida ===')
            return

        elif opt == 0:
            self.menu = 0
            return

        elif opt == 1:
            name = input('Nome da sala: ')
            theme = input('Tema da sala: ')
            ok = self.server_create_room('pub', name, theme)

        elif opt == 2:
            name = input('Nome da sala: ')
            password = input('Senha da sala: ')
            ok = self.server_create_room('priv', name, password)

        if ok:
            print(f'Código da sala criada: {self.room}')
        else:
            print('Não foi possível criar a sala')

        self.menu = 0

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
        if opt < 0 or opt > 3:
            print('=== opção inválida ===')
            return

        elif opt == 0:
            self.menu = 0
            return

        elif opt == 1:
            self.rooms = self.server_list_rooms()

        elif opt == 2:
            self.rooms = self.server_list_rooms('pub')

        elif opt == 3:
            self.rooms = self.server_list_rooms('priv')

        if self.rooms is None:
            print('Não há salas')
            return

        for room in self.rooms:
            print(room)

        self.menu = 0

    def enter_room_menu(self):
        if self.rooms is None or len(self.rooms) == 0:
            print('Não há salas, tente listá-las primeiro')

            self.menu = 0
            return

        room_password = None
        room_code = input('Código da sala: ')
        for room in self.rooms:
            if room.startswith('priv'):
                room_password = input('Senha da sala privada: ')
                break

        if self.server_enter_room(room_code, room_password):
            print('Entrou na sala')
        else:
            print('Não foi possível entrar na sala')

        self.menu = 0

    def handle_chat(self, client, message):
        ...

    def handle_canvas(self, canvas):
        ...

    def handle_draw(self):
        ...

