from game.client.base import BaseClient

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

