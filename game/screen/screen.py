from game.client.base import BaseClient

from game.screen.pages import BasePage
from game.screen.resource import Resource
from game.screen.utils.utilities import *


class Screen(BaseClient):
    def __init__(self, address, port):
        super().__init__(address, port)

        # Armazenar as "páginas" (telas) do jogo
        self.pages = {}
        self.current_page = None

        # Gerenciador de assets
        self.resource = Resource()

        pygame.init()
        pygame.freetype.init()
        path = os.path.dirname(__file__)
        # Janela
        pygame.display.set_icon(pygame.image.load(os.path.join(path, 'assets', 'ico.png')))
        pygame.display.set_caption('Gartic Golden')
        self.surface = pygame.display.set_mode((Size.SCREEN_WIDTH, Size.SCREEN_HEIGHT))
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
        self.refresh_icon = pygame.image.load(os.path.join(path, 'assets', 'refresh.png'))
        self.refresh_icon = pygame.transform.scale(self.refresh_icon, (35, 35))
        # Estado do jogo
        self.running = True
        self.current_page = 'Register'  # Página inicial - 'Register'
        self.current_input = None
        self.mouse_pos = None
        self.mouse_click = None
        self.last_click_time = 0
        self.themes = [
            'Futebol',
            'Música',
            'Animais',
            'Objetos',
            'Comidas',
            'Profissões',
            'Lugares'
        ]
        self.theme = random.choice(self.themes)
        # Dados da sala que o cliente criou
        self.words = []
        self.data_room = {}
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
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 - 315, Size.SCREEN_HEIGHT // 2 + 85, 270, 40),
                    self.font_input_chat, "Entre 1 a 20"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 + 80, Size.SCREEN_HEIGHT // 2 + 85, 270, 40),
                    self.font_input_chat, "Digite a senha da sala")
        ]
        # Jogadores e salas
        # Armazena dicionários dos jogadores da sala em que o cliente está, inclusive o seu,
        # no formato abaixo
        #
        # {
        #   'name': 'Paulo',
        #   'score': 40,
        #   'draw': False
        # }
        #
        self.players = []
        # Armazena dicionários de salas disponíveis para entrar
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
        self.rooms_start_x = Size.SCREEN_WIDTH // 2 - 330
        self.rooms_start_y = Size.SCREEN_HEIGHT // 2 - 30
        self.arrow_left_rect = pygame.Rect(60, Size.SCREEN_HEIGHT - 140, 35, 35)
        self.arrow_right_rect = pygame.Rect(Size.SCREEN_WIDTH - 110, Size.SCREEN_HEIGHT - 140, 35, 35)
        self.quant_rooms_text_pos = (Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT - 123)
        self.button_create_rect = pygame.Rect(
            Size.SCREEN_WIDTH // 2 - 94, Size.SCREEN_HEIGHT // 2 + 210, 185, 50
        )
        self.button_create_border = self.button_create_rect.inflate(2, 2)
        self.button_create_text = self.font_button.render('CRIAR SALA', True, Color.WHITE)
        self.button_create_text_rect = self.button_create_text.get_rect(center=self.button_create_rect.center)
        self.available_rooms_text = self.font_label.render('SALAS DISPONÍVEIS', True, Color.BLACK)
        self.available_rooms_pos = (Size.SCREEN_WIDTH // 2 - 150, Size.SCREEN_HEIGHT // 2 - 110)
        self.elements_cur = []
        # Página de criar sala
        self.create_logo_rect = self.image_logo_big.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 225))
        self.create_labels = [
            {'text': 'Nome da Sala', 'pos': (Size.SCREEN_WIDTH // 2 - 180, Size.SCREEN_HEIGHT // 2 - 90)},
            {'text': 'Senha', 'pos': (Size.SCREEN_WIDTH // 2 + 200, Size.SCREEN_HEIGHT // 2 + 40)},
            {'text': 'Max Rodadas', 'pos': (Size.SCREEN_WIDTH // 2 - 180, Size.SCREEN_HEIGHT // 2 + 40)},
            {'text': 'Tema', 'pos': (Size.SCREEN_WIDTH // 2 + 200, Size.SCREEN_HEIGHT // 2 - 90)}
        ]
        self.theme_rect = pygame.Rect(
            Size.SCREEN_WIDTH // 2 + 80,
            Size.SCREEN_HEIGHT // 2 - 50,
            200, 40
        )    
        self.change_theme_button = pygame.Rect(
                self.theme_rect.right + 10,
                self.theme_rect.y + (self.theme_rect.height - 30) // 2,
                30, 30
            )
        self.button_back_rect = pygame.Rect(
            Size.SCREEN_WIDTH // 2 - 272,
            Size.SCREEN_HEIGHT // 2 + 225, 
            170, 50
        )
        self.button_create_prox_rect = pygame.Rect(
            Size.SCREEN_WIDTH // 2 + 130,
            Size.SCREEN_HEIGHT // 2 + 225,
            170, 50
        )
        self.button_create_prox_text = self.font_button.render('CRIAR SALA', True, Color.WHITE)
        self.button_back_text = self.font_button.render('VOLTAR', True, Color.WHITE)

    def register_page(self, page_name, page):
        if isinstance(page, BasePage) and page_name not in self.pages:
            self.pages[page_name] = page

            # Inicializa a página com o método init
            page.init(self.surface, self.resource, self.goto_page)

    def goto_page(self, page_name):
        if page_name in self.pages:
            self.current_page = self.pages[page_name]

            # Toda vez que a página é alterada a nova página é resetada
            self.current_page.reset()

    def start(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.handle_close_game()
                else:
                    self.current_page.handle_input(event)
            #    elif event.type == pygame.MOUSEBUTTONDOWN:
            #        self.current_input = next(
            #            (input_field for input_field in self.inputs if input_field.rect.collidepoint(event.pos)), None)
            #        for input_field in self.inputs:
            #            input_field.active = input_field == self.current_input
            #    elif event.type == pygame.MOUSEWHEEL:
            #        if self.left_panel.collidepoint(pygame.mouse.get_pos()):
            #            self.scroll_offset = max(0, min(
            #                self.scroll_offset - event.y * 20, self.scroll_area.height - self.left_panel.height))
            #    if self.current_input:
            #        self.current_input.handle_event(event)

            # Atualiza a página atual
            self.current_page.update()

            # Desenha a página atual
            self.surface.fill(Color.GOLDEN)
            self.current_page.draw()
            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

    def draw(self):
        '''Filtra a sala que deve ser exibida.'''
        if self.current_page == 'Register':
            self.register_page_tmp()
        elif self.current_page == 'Rooms':
            self.rooms_page()
        elif self.current_page == 'Create':
            self.create_room_page()
        elif self.current_page == 'Play':
            self.play_page()
        self.handle_colision_cursor()
        self.handle_click_cursor()

    def register_page_tmp(self):
        '''Exibe a tela de registro onde o jogador pode inserir um apelido.'''
        self.inputs[0].draw(self.surface)
        pygame.draw.rect(self.surface, Color.BLACK, self.button_play_border, border_radius=20)
        pygame.draw.rect(self.surface, Color.GREEN, self.button_play_rect, border_radius=20)
        self.surface.blit(self.text_label_nick, self.text_label_nick_rect)
        self.surface.blit(self.image_logo_big, self.image_logo_big_rect)
        self.surface.blit(self.button_play_text, self.button_play_text_rect)

    def rooms_page(self):
        '''Exibe a tela de salas onde o jogador pode entrar ou criar uma sala.'''
        self.elements_cur.clear()
        if not self.load_rooms:
            self.get_rooms()
            self.load_rooms = True
        total_pages = max(1, (len(self.rooms) + 5) // 6)
        quant_rooms_text = 'Salas ' + (f'{self.carousel_config['current_page'] + 1}/{total_pages}' if self.rooms else f'0/0')
        quant_rooms_surface = self.font_input_chat.render(quant_rooms_text, True, Color.BLACK)
        quant_rooms_rect = quant_rooms_surface.get_rect(center=self.quant_rooms_text_pos)
        self.elements_cur.append(('button_create', self.button_create_rect))
        self.elements_cur.append(('quant_rooms_text', quant_rooms_rect))
        self.draw_rooms(total_pages)
        pygame.draw.rect(self.surface, Color.BLACK, self.button_create_border, border_radius=20)
        pygame.draw.rect(self.surface, Color.GREEN, self.button_create_rect, border_radius=20)
        self.surface.blit(self.button_create_text, self.button_create_text_rect)
        self.surface.blit(self.image_logo_big, self.image_logo_big_rect)
        self.surface.blit(self.available_rooms_text, self.available_rooms_pos)
        self.surface.blit(quant_rooms_surface, quant_rooms_rect)

    def play_page(self):
        if not self.players:
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
        pygame.draw.rect(self.surface, Color.LIGHT_GOLD,
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

        self.inputs[1].draw(self.surface)
        self.inputs[2].draw(self.surface)
        line_x = (self.inputs[1].rect.right + self.inputs[2].rect.left) // 2
        pygame.draw.line(self.surface, Color.HONEY, (line_x,
                         self.inputs[1].rect.top - 85), (line_x, self.inputs[1].rect.bottom), 2)

        button_leave = pygame.Rect(
            Size.SCREEN_WIDTH - 110, Size.SCREEN_HEIGHT - 35, 100, 30)
        pygame.draw.rect(self.surface, Color.BLACK,
                         button_leave.inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.surface, Color.RED,
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
        pygame.draw.rect(self.surface, Color.WHITE, draw_rect, border_radius=20)

        image_rect = self.image_logo_small.get_rect(
            center=(Size.SCREEN_WIDTH // 2 - 50, Size.SCREEN_HEIGHT // 2 - 250))

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        # Caso para sair da sala
        if button_leave.collidepoint(mouse_pos) and mouse_click[0]:
            if super().server_leave_room():
                self.current_page = 'Rooms'  # Página de listar as salas - Voltar
                self.data_room = {}
                self.words = []
                self.players = []
                print('Saiu da sala, sala apagada.')

        self.surface.blit(scroll_surface, (self.left_panel.x,
                         self.left_panel.y), self.left_panel)
        self.surface.blit(title_text, (12, 8))
        pygame.draw.line(self.surface, Color.HONEY, (40, 50),
                         (self.left_panel.width - 40, 50), 2)
        self.surface.blit(button_text, button_text_rect)
        self.surface.blit(self.image_logo_small, image_rect)

    def create_room_page(self):
        self.surface.blit(self.image_logo_big, self.image_logo_big_rect)
        for i, label in enumerate(self.create_labels):
            text = self.font_label.render(label['text'], True, Color.BLACK)
            self.surface.blit(text, text.get_rect(center=label['pos']))
        self.inputs[3].draw(self.surface)
        self.inputs[4].draw(self.surface)
        self.inputs[5].draw(self.surface)
        pygame.draw.rect(self.surface, Color.WHITE, self.theme_rect, border_radius=5)
        pygame.draw.rect(self.surface, Color.BLACK, self.theme_rect, 2, border_radius=5)
        theme_text = self.font_input_chat.render(self.theme, True, Color.BLACK)
        self.surface.blit(theme_text, (self.theme_rect.x + 10, self.theme_rect.y + 10))
        pygame.draw.rect(self.surface, Color.GOLDEN, self.change_theme_button, border_radius=5)
        self.surface.blit(self.refresh_icon, self.change_theme_button)
        pygame.draw.rect(self.surface, Color.BLACK, self.button_back_rect.inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.surface, Color.RED, self.button_back_rect, border_radius=20)        
        pygame.draw.rect(self.surface, Color.BLACK, self.button_create_prox_rect.inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.surface, Color.GREEN, self.button_create_prox_rect, border_radius=20)
        self.surface.blit(self.button_create_prox_text, self.button_create_prox_text.get_rect(center=self.button_create_prox_rect.center))
        self.surface.blit(self.button_back_text, self.button_back_text.get_rect(center=self.button_back_rect.center))

    def draw_rooms(self, total_pages):
        '''Desenha as salas em um carrossel (6 por página).'''
        if self.carousel_config['current_page'] != self.carousel_config['target_page']:
            direction = 1 if self.carousel_config['target_page'] > self.carousel_config['current_page'] else -1
            self.carousel_config['offset'] += direction * self.carousel_config['animation_speed'] * Size.SCREEN_WIDTH
            if abs(self.carousel_config['offset']) >= Size.SCREEN_WIDTH:
                self.carousel_config['current_page'] += direction
                self.carousel_config['offset'] = 0
        offset_direction = -1 if self.carousel_config['offset'] < 0 else 1
        for page_offset in [0, offset_direction]:
            current_page = self.carousel_config['current_page'] + page_offset
            if not 0 <= current_page < total_pages:
                continue
            start_index = current_page * 6
            end_index = min((current_page + 1) * 6, len(self.rooms))
            for i, room in enumerate(self.rooms[start_index:end_index]):
                x = self.rooms_start_x + (i % 3) * 220 + (page_offset * Size.SCREEN_WIDTH)
                y = self.rooms_start_y + (i // 3) * 100
                room_rect = pygame.Rect(x, y, 200, 80)
                self.elements_cur.append(('room', room_rect, room))
                pygame.draw.rect(self.surface, Color.WHITE, room_rect, border_radius=10)
                pygame.draw.rect(self.surface, Color.BLACK, room_rect, 2, border_radius=10)
                theme_text, _ = self.font_title_rooms.render(room['name'], fgcolor=Color.DARK_GOLDEN)
                clients_text, _ = self.font_title_rooms.render(f"{room['current_clients']}/{room['max_clients']}", fgcolor=Color.BLACK)
                info_surface = pygame.Surface(
                    (theme_text.get_width() + 10 + clients_text.get_width(),
                    max(theme_text.get_height(), clients_text.get_height())),
                    pygame.SRCALPHA
                )
                info_surface.blit(theme_text, (0, 0))
                info_surface.blit(clients_text, (theme_text.get_width() + 10, 0))
                self.surface.blit(info_surface, info_surface.get_rect(center=room_rect.center))
        if self.carousel_config['current_page'] > 0:
            self.elements_cur.append(('arrow_left', self.arrow_left_rect))
        if self.carousel_config['current_page'] < total_pages - 1:
            self.elements_cur.append(('arrow_right', self.arrow_right_rect))
        if self.carousel_config['current_page'] > 0:
            pygame.draw.polygon(self.surface, Color.BLACK, [
                (self.arrow_left_rect.left + 15, self.arrow_left_rect.centery),
                (self.arrow_left_rect.right, self.arrow_left_rect.top + 10),
                (self.arrow_left_rect.right, self.arrow_left_rect.bottom - 10)
            ])
        if self.carousel_config['current_page'] < total_pages - 1:
            pygame.draw.polygon(self.surface, Color.BLACK, [
                (self.arrow_right_rect.right - 15, self.arrow_right_rect.centery),
                (self.arrow_right_rect.left, self.arrow_right_rect.top + 10),
                (self.arrow_right_rect.left, self.arrow_right_rect.bottom - 10)
            ])

    def handle_colision_cursor(self):
        '''Atualiza o cursor do mouse com base na posição sobre os elementos.'''
        self.mouse_pos = pygame.mouse.get_pos()
        if self.current_page == 'Register':
            if self.button_play_rect.collidepoint(self.mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            elif self.inputs[0].rect.collidepoint(self.mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif self.current_page == 'Rooms':
            cursor_changed = False
            for element in self.elements_cur:
                elem_rect = element[1]
                if elem_rect.collidepoint(self.mouse_pos):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    cursor_changed = True
                    break
            if not cursor_changed:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif self.current_page == 'Create':
            if (self.button_create_prox_rect.collidepoint(self.mouse_pos) or 
                self.button_back_rect.collidepoint(self.mouse_pos) or 
                self.change_theme_button.collidepoint(self.mouse_pos)):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            elif any(input.rect.collidepoint(self.mouse_pos) for input in self.inputs[3:7]):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def handle_click_cursor(self):
        '''Verifica se o jogador clicou em algum elemento clicável.'''
        current_time = pygame.time.get_ticks()
        if current_time - self.last_click_time < 300:
            return
        mouse_click = pygame.mouse.get_pressed()[0]
        if self.current_page == 'Register':
            if (self.button_play_rect.collidepoint(self.mouse_pos)  and mouse_click and self.inputs[0].text != '') or \
            (self.inputs[0].return_pressed and self.inputs[0].text != ''):
                self.last_click_time = current_time
                self.name = self.inputs[0].text
                super().start()
                self.current_page = 'Rooms'
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                if self.current_input is not None:
                    self.current_input.active = False
                    self.current_input = None
        elif self.current_page == 'Rooms' and mouse_click:
            for element in self.elements_cur:
                elem_type, elem_rect = element[0], element[1]
                elem_type: str
                elem_rect: pygame.Rect
                if elem_rect.collidepoint(self.mouse_pos):
                    self.last_click_time = current_time
                    if elem_type == 'room':
                        room = element[2]
                        password = None if room['type'] else ''
                        # super().server_enter_room(room_code=room['code'], room_password=password)
                        # self.current_page = 'Play'
                    elif elem_type == 'arrow_left':
                        self.carousel_config['target_page'] -= 1
                    elif elem_type == 'arrow_right':
                        self.carousel_config['target_page'] += 1
                    elif elem_type == 'button_create':
                        self.current_page = 'Create'
                        self.load_rooms = False
                    elif elem_type == 'quant_rooms_text':
                        self.load_rooms = False
                    break
        elif self.current_page == 'Create' and mouse_click:
            if self.change_theme_button.collidepoint(self.mouse_pos):
                self.last_click_time = current_time
                self.theme = random.choice(self.themes)
            elif self.button_create_prox_rect.collidepoint(self.mouse_pos):
                self.last_click_time = current_time
                data_room = [input_field.text for input_field in self.inputs[3:5]]
                if all(data_room):  # Criando uma sala
                    name, max_rounds = data_room
                    max_rounds = int(max_rounds)
                    if max_rounds < 1 or max_rounds > 20: # Como tem 20 palavras de cada tema, só pode ter até no máximo 20 rodadas
                        return
                    password = self.inputs[5].text
                    room_type = 'pub' if password == '' else 'priv'
                    # Usando tema como nome por enquanto
                    super().server_create_room(room_type, self.theme, password if password else None)
                    self.current_page = 'Play'
                    self.words = load_words(self.theme, max_rounds)
                    self.players.append({'name': self.name, 'score': 0, 'draw': False})
                    self.data_room = {'name': name, 'theme': self.theme, 'tipo': room_type, 'max_rounds': max_rounds}
                    # Resetar os inputs
                    for input_field in self.inputs[3:5]:
                        input_field.text = ''
            elif self.button_back_rect.collidepoint(self.mouse_pos):
                self.last_click_time = current_time
                self.current_page = 'Rooms'
                for input_field in self.inputs[3:6]:
                    input_field.text = ''
                    input_field.active = False

    def handle_close_game(self):
        '''Finaliza o jogo, removendo o cliente da sala (se estiver em uma) e do servidor.'''
        self.running = False
        if self.room:
            super().server_leave_room()
        if self.current_page != 'Register':
            super().server_unregister()
    
    def get_rooms(self, args=None):
        '''Carrega as sala de acordo com args.'''
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
    
    def get_players(self):
        '''Carrega os jogadores da sala que o cliente está.'''
        ...

    def handle_chat(self, client, message):
        print(f'~{client["name"]}: {message}')

    def handle_canvas(self, canvas):
        print(f'canvas: {canvas}')
