import os
from game.client.base import BaseClient
from game.screen.utils.utilities import *

class Screen(BaseClient):
    def __init__(self, address, port):
        super().__init__(address, port)
        pygame.init()
        pygame.freetype.init()
        path = os.path.dirname(__file__)
        # Janela
        pygame.display.set_icon(pygame.image.load(os.path.join(path, 'assets', 'ico.png')))
        pygame.display.set_caption('Gartic Golden')
        self.screen = pygame.display.set_mode((Size.SCREEN_WIDTH, Size.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        # Fontes
        self.font_label = pygame.font.Font(os.path.join(path, 'font', 'Acme-Regular.ttf'), 40)
        self.font_button = pygame.font.Font(os.path.join(path, 'font', 'Acme-Regular.ttf'), 30)
        self.font_input_name = pygame.font.Font(os.path.join(path, 'font', 'Acme-Regular.ttf'), 26)
        self.font_title_rooms = pygame.freetype.Font(os.path.join(path, 'font', 'Acme-Regular.ttf'), 19)
        self.font_title_rooms.strong = True
        self.font_input_chat = pygame.font.Font(os.path.join(path, 'font', 'Acme-Regular.ttf'), 18)
        # Imagens
        self.image_logo_big = pygame.image.load(os.path.join(path, 'assets', 'logo.png'))
        self.image_logo_small = pygame.image.load(os.path.join(path, 'assets', 'logo_small.png'))
        self.icon_user = pygame.image.load(os.path.join(path, 'assets', 'user.png'))
        self.user_icon = pygame.transform.scale(self.icon_user, (30, 30))
        self.pencil = pygame.image.load(os.path.join(path, 'assets', 'pencil.png'))
        self.pencil_icon = pygame.transform.scale(self.pencil, (20, 20))
        # Estado do jogo
        self.running = True
        self.current_page = 'Register'  # Página inicial - 'Register'
        self.current_input = None
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_click = pygame.mouse.get_pressed()
        # Configuração do carrossel
        self.carousel_config = {
            'current_page': 0, 'target_page': 0, 'offset': 0, 'animation_speed': 0.1
        }
        # Painel lateral de jogadores
        self.left_panel = pygame.Rect(0, 50, Size.SCREEN_WIDTH // 5 - 5, Size.SCREEN_HEIGHT)
        # Campos de entrada
        self.inputs = [
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 - 150, Size.SCREEN_HEIGHT // 2, 300, 40),
                    self.font_input_name, "Digite seu nick"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 - 185, Size.SCREEN_HEIGHT - 85, 250, 35),
                    self.font_input_chat, "Digite sua resposta"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 + 95, Size.SCREEN_HEIGHT - 85, 250, 35),
                    self.font_input_chat, "Converse no Chat"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 - 315, Size.SCREEN_HEIGHT // 2 - 50, 270, 40),
                    self.font_input_chat, "Digite o nome da sala"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 + 80, Size.SCREEN_HEIGHT // 2 - 50, 270, 40),
                    self.font_input_chat, "Escolha o tema da sala"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 - 315, Size.SCREEN_HEIGHT // 2 + 85, 270, 40),
                    self.font_input_chat, "Escolha o máximo de jogadores"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 + 80, Size.SCREEN_HEIGHT // 2 + 85, 270, 40),
                    self.font_input_chat, "Digite a senha da sala")
        ]
        # Jogadores e salas
        self.players = []
        self.rooms = []
        # Logo grande
        self.image_logo_big_rect = self.image_logo_big.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 200)
        )
        # Página de registro
        self.text_label_nick = self.font_label.render('DIGITE SEU NICK', True, Color.BLACK)
        self.text_label_nick_rect = self.text_label_nick.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 50)
        )
        self.button_play_rect = pygame.Rect(
            Size.SCREEN_WIDTH // 2 - 100, Size.SCREEN_HEIGHT // 2 + 100, 200, 50
        )
        self.button_play_border = self.button_play_rect.inflate(2, 2)
        self.button_play_text = self.font_button.render('JOGAR', True, Color.WHITE)
        self.button_play_text_rect = self.button_play_text.get_rect(center=self.button_play_rect.center)
        # Página de listar salas
        self.load_rooms = False

    def start(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.handle_close_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.current_input = next(
                        (input_field for input_field in self.inputs if input_field.rect.collidepoint(event.pos)), None)
                    for input_field in self.inputs:
                        input_field.active = input_field == self.current_input
                elif event.type == pygame.MOUSEWHEEL:
                    if self.left_panel.collidepoint(pygame.mouse.get_pos()):
                        self.scroll_offset = max(0, min(
                            self.scroll_offset - event.y * 20, self.scroll_area.height - self.left_panel.height))
                if self.current_input:
                    self.current_input.handle_event(event)

            self.screen.fill(Color.GOLDEN)
            self.draw()
            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

    def draw(self):
        if self.current_page == 'Register':
            self.register_page()
        elif self.current_page == 'Rooms':
            self.rooms_page()
        elif self.current_page == 'Create':
            self.create_room_page()
        elif self.current_page == 'Play':
            self.play_page()
        elif self.current_page == 'Test':
            self.play_page()
        self.handle_colision_cursor()
        self.handle_prox_page()

    def register_page(self):
        '''Exibe a tela de registro onde o jogador pode inserir um apelido.'''
        self.inputs[0].draw(self.screen)
        pygame.draw.rect(self.screen, Color.BLACK, self.button_play_border, border_radius=20)
        pygame.draw.rect(self.screen, Color.GREEN, self.button_play_rect, border_radius=20)
        self.screen.blit(self.text_label_nick, self.text_label_nick_rect)
        self.screen.blit(self.image_logo_big, self.image_logo_big_rect)
        self.screen.blit(self.button_play_text, self.button_play_text_rect)

    def rooms_page(self):
        if self.rooms == [] and not self.load_rooms:
            self.get_rooms()
            self.load_rooms = True

        total_pages = (len(self.rooms) + 6 - 1) // 6
        if self.carousel_config['current_page'] != self.carousel_config['target_page']:
            direction = 1 if self.carousel_config['target_page'] > self.carousel_config['current_page'] else -1
            self.carousel_config['offset'] += direction * \
                self.carousel_config['animation_speed'] * Size.SCREEN_WIDTH
            if abs(self.carousel_config['offset']) >= Size.SCREEN_WIDTH:
                self.carousel_config['current_page'] += direction
                self.carousel_config['offset'] = 0
        else:
            self.carousel_config['offset'] = 0
        arrow_left = pygame.Rect(60, Size.SCREEN_HEIGHT - 140, 35, 35)
        arrow_right = pygame.Rect(
            Size.SCREEN_WIDTH - 110, Size.SCREEN_HEIGHT - 140, 35, 35)

        page_text = f"Salas {0 if total_pages == 0 else self.carousel_config['current_page'] + 1}/{total_pages}"
        text_page = self.font_input_chat.render(page_text, True, Color.BLACK)
        text_rect = text_page.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT - 123))
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        cursor_room = False
        start_x = Size.SCREEN_WIDTH // 2 - 330 + \
            int(self.carousel_config['offset'])
        start_y = Size.SCREEN_HEIGHT // 2 - 30
        cursor_room = False
        offset_direction = -1 if self.carousel_config['offset'] < 0 else 1

        if total_pages > 1 and self.carousel_config['current_page'] == self.carousel_config['target_page']:
            if arrow_left.collidepoint(mouse_pos) and mouse_click[0] and self.carousel_config['current_page'] > 0:
                self.carousel_config['target_page'] -= 1
            if arrow_right.collidepoint(mouse_pos) and mouse_click[0] and self.carousel_config['current_page'] < total_pages - 1:
                self.carousel_config['target_page'] += 1
        for page_offset in [0, offset_direction]:
            current_page = self.carousel_config['current_page'] + page_offset
            if not (0 <= current_page < total_pages):
                continue
            start_index, end_index = current_page * \
                6, min((current_page + 1) * 6, len(self.rooms))
            for i, room in enumerate(self.rooms[start_index:end_index]):
                x = start_x + (i % 3) * 220 + (page_offset * Size.SCREEN_WIDTH)
                y = start_y + (i // 3) * 100
                room_rect = pygame.Rect(x, y, 200, 80)

                if room_rect.collidepoint(mouse_pos):
                    cursor_room = True
                    if mouse_click[0]:
                        # Aqui fica a lógica para entrar na sala
                        # Terá algo como self.current_page = 'Play'
                        print('ENTROU NA SALA')

                pygame.draw.rect(self.screen, Color.WHITE,
                                 room_rect, border_radius=10)
                pygame.draw.rect(self.screen, Color.BLACK,
                                 room_rect, 2, border_radius=10)
                theme, _ = self.font_title_rooms.render(
                    room['name'], fgcolor=Color.DARK_GOLDEN)
                max_clients, _ = self.font_title_rooms.render(
                    f'{room['max_clients']}/10', fgcolor=Color.BLACK)
                info = pygame.Surface(
                    (theme.get_width() + 10 + max_clients.get_width(),
                     max(theme.get_height(), max_clients.get_height())),
                    pygame.SRCALPHA
                )
                info.blit(theme, (0, 0))
                info.blit(
                    max_clients, (theme.get_width() + 10, 0))
                self.screen.blit(info, info.get_rect(
                    center=room_rect.center))

        draw_arrow_left = self.carousel_config['current_page'] > 0
        draw_arrow_right = self.carousel_config['current_page'] < total_pages - 1
        if draw_arrow_left:
            pygame.draw.polygon(self.screen, Color.BLACK, [
                (arrow_left.left + 15, arrow_left.centery),
                (arrow_left.right, arrow_left.top + 10),
                (arrow_left.right, arrow_left.bottom - 10)
            ])

        if draw_arrow_right:
            pygame.draw.polygon(self.screen, Color.BLACK, [
                (arrow_right.right - 15, arrow_right.centery),
                (arrow_right.left, arrow_right.top + 10),
                (arrow_right.left, arrow_right.bottom - 10)
            ])
        if draw_arrow_left and arrow_left.collidepoint(mouse_pos):
            cursor_room = True
        if draw_arrow_right and arrow_right.collidepoint(mouse_pos):
            cursor_room = True

        self.screen.blit(text_page, text_rect)
        button_create = pygame.Rect(
            Size.SCREEN_WIDTH // 2 - 94, Size.SCREEN_HEIGHT // 2 + 210, 185, 50)
        pygame.draw.rect(self.screen, Color.BLACK,
                         button_create.inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.screen, Color.GREEN,
                         button_create, border_radius=20)
        button_text = self.font_button.render('CRIAR SALA', True, Color.WHITE)
        self.screen.blit(button_text, button_text.get_rect(
            center=button_create.center))
        self.screen.blit(self.image_logo_big, self.image_logo_big.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 200)))
        self.screen.blit(self.font_label.render('SALAS DISPONÍVEIS', True, Color.BLACK),
                         (Size.SCREEN_WIDTH // 2 - 150, Size.SCREEN_HEIGHT // 2 - 110))

        if button_create.collidepoint(mouse_pos):
            cursor_room = True
            if mouse_click[0]:
                self.current_page = 'Create'

        pygame.mouse.set_cursor(
            pygame.SYSTEM_CURSOR_HAND if cursor_room else pygame.SYSTEM_CURSOR_ARROW)

    def play_page(self):
        # Aqui onde eu preparo os jogadores da sala
        # Uma lista de dicionários que serão os jogadores, com chaves como 'name', 'score', 'draw' e 'active'
        self.players = []

        if not self.players:  # Proteção para caso entre aqui sem nenhum jogador, o que não será possível
            return

        if not hasattr(self, 'scroll_area'):
            total_height = Size.SCREEN_HEIGHT if len(
                self.players) < 8 else len(self.players) * 70 + 60
            self.scroll_area = pygame.Rect(
                self.left_panel.x,
                self.left_panel.y,
                self.left_panel.width,
                min(total_height, Size.SCREEN_HEIGHT * 2)
            )
            self.scroll_offset = 0

        pygame.draw.rect(self.screen, Color.LIGHT_GOLD,
                         pygame.Rect(0, 0, self.left_panel.width, 50))
        title_text = self.font_input_name.render(
            'JOGADORES', True, Color.BLACK)

        scroll_surface = pygame.Surface(
            (self.left_panel.width, self.scroll_area.height))
        scroll_surface.fill(Color.LIGHT_GOLD)

        for i, player in enumerate(self.players):
            y_pos = 60 + i * 70 - self.scroll_offset
            pygame.draw.rect(scroll_surface, Color.GOLDEN, (10, y_pos,
                             self.left_panel.width - 20, 60), border_radius=5)
            scroll_surface.blit(self.user_icon, (20, y_pos + 15))
            name_text = self.font_input_chat.render(
                player['name'], True, Color.BLACK)
            scroll_surface.blit(name_text, (60, y_pos + 10))
            score_text = self.font_input_chat.render(
                f"{player['score']} pts", True, Color.BLACK)
            scroll_surface.blit(
                score_text, (self.left_panel.width - 94, y_pos + 32))
            if player['draw']:
                scroll_surface.blit(
                    self.pencil_icon, (self.left_panel.width - 32, y_pos + 36))

        self.inputs[1].draw(self.screen)
        self.inputs[2].draw(self.screen)
        line_x = (self.inputs[1].rect.right + self.inputs[2].rect.left) // 2
        pygame.draw.line(self.screen, Color.HONEY, (line_x,
                         self.inputs[1].rect.top - 85), (line_x, self.inputs[1].rect.bottom), 2)

        button_leave = pygame.Rect(
            Size.SCREEN_WIDTH - 110, Size.SCREEN_HEIGHT - 35, 100, 30)
        pygame.draw.rect(self.screen, Color.BLACK,
                         button_leave.inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.screen, Color.RED,
                         button_leave, border_radius=20)

        button_text = self.font_button.render('Sair', True, Color.WHITE)
        button_text_rect = button_text.get_rect(center=button_leave.center)

        # Cursor diferente para o mouse colidindo com o botão ou input
        mouse_pos = pygame.mouse.get_pos()
        if button_leave.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.inputs[1].rect.collidepoint(mouse_pos) or self.inputs[2].rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Área de desenho
        draw_rect = pygame.Rect(
            Size.SCREEN_WIDTH // 4 - 40,
            Size.SCREEN_HEIGHT // 4 - 55,
            Size.SCREEN_WIDTH - 175,
            Size.SCREEN_HEIGHT // 2 + 30
        )
        pygame.draw.rect(self.screen, Color.WHITE, draw_rect, border_radius=20)

        image_rect = self.image_logo_small.get_rect(
            center=(Size.SCREEN_WIDTH // 2 - 50, Size.SCREEN_HEIGHT // 2 - 250))

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        # Caso para sair da sala
        if button_leave.collidepoint(mouse_pos) and mouse_click[0]:
            res = super().server_leave_room()
            if res:
                self.current_page = 'Rooms'  # Página de listar as salas - Voltar

        self.screen.blit(scroll_surface, (self.left_panel.x,
                         self.left_panel.y), self.left_panel)
        self.screen.blit(title_text, (12, 8))
        pygame.draw.line(self.screen, Color.HONEY, (40, 50),
                         (self.left_panel.width - 40, 50), 2)
        self.screen.blit(button_text, button_text_rect)
        self.screen.blit(self.image_logo_small, image_rect)

    def create_room_page(self):
        image_rect = self.image_logo_big.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 225))

        labels = ['Nome da Sala', 'Tema', 'Max Jogadores', 'Senha']
        for i, label in enumerate(labels):
            row = 0 if i < 2 else 1
            col = i % 2
            x_pos = Size.SCREEN_WIDTH // 2 - 180 + \
                (col * 380)  # 250 é o espaçamento entre colunas
            y_pos = Size.SCREEN_HEIGHT // 2 - 90 + \
                (row * 130)  # 110 é o espaçamento entre linhas

            text = self.font_label.render(label, True, Color.BLACK)
            text_rect = text.get_rect(center=(x_pos, y_pos))
            self.screen.blit(text, text_rect)
            self.inputs[i + 3].draw(self.screen)

        button_back = pygame.Rect(Size.SCREEN_WIDTH // 2 - 272,
                                  Size.SCREEN_HEIGHT // 2 + 225, 170, 50)
        pygame.draw.rect(self.screen, Color.BLACK,
                         button_back.inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.screen, Color.RED, button_back, border_radius=20)

        button_create = pygame.Rect(Size.SCREEN_WIDTH // 2 + 130,
                                    Size.SCREEN_HEIGHT // 2 + 225, 170, 50)
        pygame.draw.rect(self.screen, Color.BLACK,
                         button_create.inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.screen, Color.GREEN,
                         button_create, border_radius=20)

        button_create_text = self.font_button.render(
            'CRIAR SALA', True, Color.WHITE)
        button_create_rect = button_create_text.get_rect(
            center=button_create.center)

        button_back_text = self.font_button.render('VOLTAR', True, Color.WHITE)
        button_back_rect = button_back_text.get_rect(center=button_back.center)

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        # Cursor diferente para o mouse colidindo com o botão ou input
        if button_create.collidepoint(mouse_pos) or button_back.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif any(input.rect.collidepoint(mouse_pos) for input in self.inputs[3:7]):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        data_room = [input_field.text for input_field in self.inputs[3:6]]
        if all(data_room) and button_create.collidepoint(mouse_pos) and mouse_click[0]:
            name, theme, max_clients = data_room
            password = self.inputs[6].text
            type_room = 'pub' if password == '' else 'priv'
            # Lógica para criar a sala aqui
            print(f"Criando sala: (Nome: {name} |Tipo: {type_room})")
        elif button_back.collidepoint(mouse_pos) and mouse_click[0]:
            self.current_page = 'Rooms'
            self.load_rooms = False
            for input_field in self.inputs[3:7]:
                input_field.text = ''
                input_field.active = False

        self.screen.blit(self.image_logo_big, image_rect)
        self.screen.blit(button_create_text, button_create_rect)
        self.screen.blit(button_back_text, button_back_rect)

    def handle_colision_cursor(self):
        '''Atualiza o cursor do mouse com base na posição sobre os elementos.'''
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_click = pygame.mouse.get_pressed()
        if self.current_page == 'Register':
            if self.button_play_rect.collidepoint(self.mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            elif self.inputs[0].rect.collidepoint(self.mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def handle_prox_page(self):
        '''Verifica se o jogador deve mudar de página.'''
        if self.current_page == 'Register':
            if (self.button_play_rect.collidepoint(self.mouse_pos) and self.mouse_click[0] and self.inputs[0].text != '') or \
            (self.inputs[0].return_pressed and self.inputs[0].text != ''):
                self.name = self.inputs[0].text
                super().start()
                self.current_page = 'Rooms'
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                if self.current_input is not None:
                    self.current_input.active = False
                    self.current_input = None

    def handle_close_game(self):
        '''Finaliza o jogo, removendo o cliente da sala (se estiver em uma) e do servidor.'''
        self.running = False
        if self.room:
            super().server_leave_room()
        super().server_unregister()
    
    def get_rooms(self, args=None):
        """Carrega as sala."""
        rooms = super().server_list_rooms(args)
        self.rooms = []
        if len(rooms) == 1 and rooms[0] == '':
            return
        for line in rooms[:-1]:
            data = line.strip().split(",")
            room_data = {
                "type": data[0],
                "name": data[1],
                "code": data[2],
                "current_clients": data[3],
                "max_clients": data[4]
            }
            self.rooms.append(room_data)

    def handle_chat(self, client, message):
        print(f'~{client["name"]}: {message}')

    def handle_canvas(self, canvas):
        print(f'canvas: {canvas}')
