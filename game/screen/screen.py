from game.client.base import BaseClient
from game.screen.utils.utilities import *


class Screen(BaseClient):
    def __init__(self, address, port):
        super().__init__(address, port)
        pygame.init()
        pygame.freetype.init()
        path = os.path.dirname(__file__)
        # Janela
        pygame.display.set_icon(pygame.image.load(
            os.path.join(path, 'assets', 'ico.png')))
        pygame.display.set_caption('Gartic Golden')
        self.screen = pygame.display.set_mode(
            (Size.SCREEN_WIDTH, Size.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        # Fontes
        self.font_label = pygame.font.Font(
            os.path.join(path, 'font', 'Acme-Regular.ttf'), 40)
        self.font_button = pygame.font.Font(
            os.path.join(path, 'font', 'Acme-Regular.ttf'), 30)
        self.font_input_name = pygame.font.Font(
            os.path.join(path, 'font', 'Acme-Regular.ttf'), 26)
        self.font_title_rooms = pygame.freetype.Font(
            os.path.join(path, 'font', 'Acme-Regular.ttf'), 19)
        self.font_title_rooms.strong = True
        self.font_input_chat = pygame.font.Font(
            os.path.join(path, 'font', 'Acme-Regular.ttf'), 18)
        # Imagens
        self.image_logo_big = pygame.image.load(
            os.path.join(path, 'assets', 'logo.png'))
        self.image_logo_small = pygame.image.load(
            os.path.join(path, 'assets', 'logo_small.png'))
        self.icon_user = pygame.image.load(
            os.path.join(path, 'assets', 'user.png'))
        self.user_icon = pygame.transform.scale(self.icon_user, (30, 30))
        self.pencil = pygame.image.load(
            os.path.join(path, 'assets', 'pencil.png'))
        self.pencil_icon = pygame.transform.scale(self.pencil, (20, 20))
        self.refresh_icon = pygame.image.load(
            os.path.join(path, 'assets', 'refresh.png'))
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
        # Configuração do carrossel
        self.carousel_config = {
            'current_page': 0, 'target_page': 0, 'offset': 0, 'animation_speed': 0.1
        }
        # Painel lateral de jogadores
        self.left_panel = pygame.Rect(
            0, 50, Size.SCREEN_WIDTH // 5 - 5, Size.SCREEN_HEIGHT)
        # Campos de entrada
        self.inputs = [
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 - 150, Size.SCREEN_HEIGHT // 2, 300, 40),
                       self.font_input_name, "Entre 1 e 7 caracteres"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 - 185, Size.SCREEN_HEIGHT - 85, 250, 35),
                       self.font_input_chat, "Digite sua resposta"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 + 95, Size.SCREEN_HEIGHT - 85, 250, 35),
                       self.font_input_chat, "Converse no Chat"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 - 315, Size.SCREEN_HEIGHT // 2 - 50, 270, 40),
                       self.font_input_chat, "Entre 1 e 12 caracteres"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 - 315, Size.SCREEN_HEIGHT // 2 + 85, 270, 40),
                       self.font_input_chat, "Entre 1 a 20"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 + 80, Size.SCREEN_HEIGHT // 2 + 85, 270, 40),
                       self.font_input_chat, "Digite a senha da sala")
        ]
        # Jogadores e salas
        # Armazena dicionários de salas disponíveis para entrar
        self.rooms = []
        # Logo grande
        self.image_logo_big_rect = self.image_logo_big.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 200)
        )
        # Página de registro
        self.text_label_nick = self.font_label.render(
            'DIGITE SEU NICK', True, Color.BLACK)
        self.text_label_nick_rect = self.text_label_nick.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 50)
        )
        self.button_play_rect = pygame.Rect(
            Size.SCREEN_WIDTH // 2 - 100, Size.SCREEN_HEIGHT // 2 + 100, 200, 50
        )
        self.button_play_border = self.button_play_rect.inflate(2, 2)
        self.button_play_text = self.font_button.render(
            'JOGAR', True, Color.WHITE)
        self.button_play_text_rect = self.button_play_text.get_rect(
            center=self.button_play_rect.center)
        # Página de listar salas
        self.load_rooms = False
        self.rooms_start_x = Size.SCREEN_WIDTH // 2 - 330
        self.rooms_start_y = Size.SCREEN_HEIGHT // 2 - 30
        self.arrow_left_rect = pygame.Rect(
            60, Size.SCREEN_HEIGHT - 140, 35, 35)
        self.arrow_right_rect = pygame.Rect(
            Size.SCREEN_WIDTH - 110, Size.SCREEN_HEIGHT - 140, 35, 35)
        self.quant_rooms_text_pos = (
            Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT - 123)
        self.button_create_rect = pygame.Rect(
            Size.SCREEN_WIDTH // 2 - 94, Size.SCREEN_HEIGHT // 2 + 210, 185, 50
        )
        self.button_create_border = self.button_create_rect.inflate(2, 2)
        self.button_create_text = self.font_button.render(
            'CRIAR SALA', True, Color.WHITE)
        self.button_create_text_rect = self.button_create_text.get_rect(
            center=self.button_create_rect.center)
        self.available_rooms_text = self.font_label.render(
            'SALAS DISPONÍVEIS', True, Color.BLACK)
        self.available_rooms_pos = (
            Size.SCREEN_WIDTH // 2 - 150, Size.SCREEN_HEIGHT // 2 - 110)
        self.elements_cur = []
        # Página de criar sala
        self.create_logo_rect = self.image_logo_big.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 225))
        self.create_labels = [
            {'text': 'Nome da Sala', 'pos': (
                Size.SCREEN_WIDTH // 2 - 180, Size.SCREEN_HEIGHT // 2 - 90)},
            {'text': 'Senha', 'pos': (
                Size.SCREEN_WIDTH // 2 + 200, Size.SCREEN_HEIGHT // 2 + 40)},
            {'text': 'Max Rodadas', 'pos': (
                Size.SCREEN_WIDTH // 2 - 180, Size.SCREEN_HEIGHT // 2 + 40)},
            {'text': 'Tema', 'pos': (
                Size.SCREEN_WIDTH // 2 + 200, Size.SCREEN_HEIGHT // 2 - 90)}
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
        self.button_create_prox_text = self.font_button.render(
            'CRIAR SALA', True, Color.WHITE)
        self.button_back_text = self.font_button.render(
            'VOLTAR', True, Color.WHITE)
        # Página de jogar
        self.play_elements = {
            'title_text': self.font_input_name.render('JOGADORES', True, Color.BLACK),
            'button_leave': pygame.Rect(Size.SCREEN_WIDTH - 110, Size.SCREEN_HEIGHT - 35, 100, 30),
            'button_leave_text': self.font_button.render('Sair', True, Color.WHITE),
            'draw_rect': pygame.Rect(
                Size.SCREEN_WIDTH // 4 - 40,
                Size.SCREEN_HEIGHT // 4 - 55,
                Size.SCREEN_WIDTH - 175,
                Size.SCREEN_HEIGHT // 2 + 30
            ),
            'image_rect': self.image_logo_small.get_rect(
                center=(Size.SCREEN_WIDTH // 2 - 50, Size.SCREEN_HEIGHT // 2 - 250)),
            'line_x': (self.inputs[1].rect.right + self.inputs[2].rect.left) // 2
        }
        self.scroll_area_players_rect = pygame.Rect(
            0, 50,
            Size.SCREEN_WIDTH // 5 - 5,
            Size.SCREEN_HEIGHT  # Valor inicial padrão
        )
        self.scroll_offset = 0
        self.chat_all_rect = pygame.Rect(
            self.inputs[2].rect.x,
            self.inputs[2].rect.y - 90,
            self.inputs[2].rect.width - 5,
            88
        )
        self.chat_all_scroll = 0

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
                    if self.current_page == 'Play':
                        if self.chat_all_rect.collidepoint(pygame.mouse.get_pos()):
                            self.chat_all_scroll = max(
                                0, self.chat_all_scroll - event.y)
                        elif self.left_panel.collidepoint(pygame.mouse.get_pos()):
                            self.scroll_offset = max(0, min(
                                self.scroll_offset - event.y * 20, self.scroll_area_players_rect.height - self.left_panel.height))
                if self.current_input:
                    self.current_input.handle_event(event)

            self.screen.fill(Color.GOLDEN)
            self.draw()
            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

    def draw(self):
        '''Filtra a sala que deve ser exibida.'''
        if self.current_page == 'Register':
            self.register_page()
        elif self.current_page == 'Rooms':
            self.rooms_page()
        elif self.current_page == 'Create':
            self.create_room_page()
        elif self.current_page == 'Play':
            self.play_page()
            self.handle_chat()
        self.handle_colision_cursor()
        self.handle_click_cursor()

    def register_page(self):
        '''Exibe a tela de registro onde o jogador pode inserir um apelido.'''
        self.inputs[0].draw(self.screen)
        pygame.draw.rect(self.screen, Color.BLACK,
                         self.button_play_border, border_radius=20)
        pygame.draw.rect(self.screen, Color.GREEN,
                         self.button_play_rect, border_radius=20)
        self.screen.blit(self.text_label_nick, self.text_label_nick_rect)
        self.screen.blit(self.image_logo_big, self.image_logo_big_rect)
        self.screen.blit(self.button_play_text, self.button_play_text_rect)

    def rooms_page(self):
        '''Exibe a tela de salas onde o jogador pode entrar ou criar uma sala.'''
        self.elements_cur.clear()
        if not self.load_rooms:
            self.get_rooms()
            self.load_rooms = True
        total_pages = max(1, (len(self.rooms) + 5) // 6)
        quant_rooms_text = 'Salas ' + \
            (f'{self.carousel_config['current_page'] + 1}/{total_pages}' if self.rooms else f'0/0')
        quant_rooms_surface = self.font_input_chat.render(
            quant_rooms_text, True, Color.BLACK)
        quant_rooms_rect = quant_rooms_surface.get_rect(
            center=self.quant_rooms_text_pos)
        self.elements_cur.append(('button_create', self.button_create_rect))
        self.elements_cur.append(('quant_rooms_text', quant_rooms_rect))
        self.draw_rooms(total_pages)
        pygame.draw.rect(self.screen, Color.BLACK,
                         self.button_create_border, border_radius=20)
        pygame.draw.rect(self.screen, Color.GREEN,
                         self.button_create_rect, border_radius=20)
        self.screen.blit(self.button_create_text, self.button_create_text_rect)
        self.screen.blit(self.image_logo_big, self.image_logo_big_rect)
        self.screen.blit(self.available_rooms_text, self.available_rooms_pos)
        self.screen.blit(quant_rooms_surface, quant_rooms_rect)

    def play_page(self):
        '''Página principal do jogo.'''
        if not self.room_clients:
            return
        total_height = Size.SCREEN_HEIGHT if len(
            self.room_clients) < 8 else len(self.room_clients) * 70 + 60
        self.scroll_area_players_rect.height = min(
            total_height, Size.SCREEN_HEIGHT * 2)
        pygame.draw.rect(self.screen, Color.LIGHT_GOLD,
                         pygame.Rect(0, 0, self.left_panel.width, 50))

        scroll_area_players = pygame.Surface(
            (self.left_panel.width, self.scroll_area_players_rect.height))
        scroll_area_players.fill(Color.LIGHT_GOLD)
        self.draw_card_players(scroll_area_players)
        self.inputs[1].draw(self.screen)
        self.inputs[2].draw(self.screen)
        self.draw_chat_all()
        pygame.draw.line(self.screen, Color.HONEY,
                         (self.play_elements['line_x'],
                          self.inputs[1].rect.top - 85),
                         (self.play_elements['line_x'], self.inputs[1].rect.bottom), 2)
        pygame.draw.rect(self.screen, Color.BLACK,
                         self.play_elements['button_leave'].inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.screen, Color.RED,
                         self.play_elements['button_leave'], border_radius=20)
        pygame.draw.rect(self.screen, Color.WHITE,
                         self.play_elements['draw_rect'], border_radius=20)
        self.screen.blit(scroll_area_players, (self.left_panel.x,
                         self.left_panel.y), self.left_panel)
        self.screen.blit(self.play_elements['title_text'], (12, 8))
        pygame.draw.line(self.screen, Color.HONEY, (40, 50),
                         (self.left_panel.width - 40, 50), 2)
        self.screen.blit(self.play_elements['button_leave_text'],
                         self.play_elements['button_leave_text'].get_rect(
            center=self.play_elements['button_leave'].center))
        self.screen.blit(self.image_logo_small,
                         self.play_elements['image_rect'])

    def draw_card_players(self, area):
        """Desenha os cards dos jogadores no painel."""
        ord_players = sorted(
            self.room_clients.items(),
            key=lambda item: item[1]['score'],
            reverse=True
        )
        for i, (_, client_data) in enumerate(ord_players):
            y_pos = 60 + i * 70 - self.scroll_offset
            pygame.draw.rect(
                area,
                Color.GOLDEN,
                (10, y_pos, self.left_panel.width - 20, 60),
                border_radius=5
            )
            area.blit(self.user_icon, (20, y_pos + 15))
            name_text = self.font_input_chat.render(
                client_data['name'],
                True,
                Color.DARK_GREEN if client_data['self'] else Color.BLACK
            )
            area.blit(name_text, (60, y_pos + 10))
            score_text = self.font_input_chat.render(
                f"{client_data['score']} pts",
                True,
                Color.BLACK
            )
            area.blit(score_text, (self.left_panel.width - 94, y_pos + 32))
            if client_data['state'] == 'draw':
                area.blit(self.pencil_icon,
                          (self.left_panel.width - 32, y_pos + 36))

    def draw_chat_all(self):
        msgs = [(msg[:12], client['name'], client['self']) for client in self.room_clients.values() for msg in client['msgs']]
        total = len(msgs)
        scroll_max = max(0, total - 4)
        self.chat_all_scroll = max(0, min(self.chat_all_scroll, scroll_max))
        pygame.draw.rect(self.screen, Color.LIGHT_GOLD, self.chat_all_rect, border_radius=5)
        old = self.screen.get_clip()
        self.screen.set_clip(self.chat_all_rect)
        for i in range(4):
            idx = total - 1 - (i + self.chat_all_scroll)
            if idx < 0: continue
            msg, sender, is_self = msgs[idx]
            prefix = "Você" if is_self else sender
            color = Color.DARK_GREEN if is_self else Color.BLACK
            text = f"{prefix}: {msg}"
            surface = self.font_input_chat.render(text, True, color)
            y = self.chat_all_rect.bottom - 5 - ((i+1)*18)
            x = self.chat_all_rect.right - 25 - surface.get_width() if is_self else self.chat_all_rect.left + 25
            self.screen.blit(surface, (x, y))
        self.screen.set_clip(old)
        if total > 4:
            h = max(10, (4/total)*self.chat_all_rect.height)
            pos = (self.chat_all_scroll/scroll_max)*(self.chat_all_rect.height-h)
            pygame.draw.rect(self.screen, Color.DARK_GOLDEN,
                            (self.chat_all_rect.right-6, self.chat_all_rect.y + pos, 4, h), border_radius=2)


    def create_room_page(self):
        self.screen.blit(self.image_logo_big, self.image_logo_big_rect)
        for i, label in enumerate(self.create_labels):
            text = self.font_label.render(label['text'], True, Color.BLACK)
            self.screen.blit(text, text.get_rect(center=label['pos']))
        self.inputs[3].draw(self.screen)
        self.inputs[4].draw(self.screen)
        self.inputs[5].draw(self.screen)
        pygame.draw.rect(self.screen, Color.WHITE,
                         self.theme_rect, border_radius=5)
        pygame.draw.rect(self.screen, Color.BLACK,
                         self.theme_rect, 2, border_radius=5)
        theme_text = self.font_input_chat.render(self.theme, True, Color.BLACK)
        self.screen.blit(theme_text, (self.theme_rect.x +
                         10, self.theme_rect.y + 10))
        pygame.draw.rect(self.screen, Color.GOLDEN,
                         self.change_theme_button, border_radius=5)
        self.screen.blit(self.refresh_icon, self.change_theme_button)
        pygame.draw.rect(self.screen, Color.BLACK,
                         self.button_back_rect.inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.screen, Color.RED,
                         self.button_back_rect, border_radius=20)
        pygame.draw.rect(self.screen, Color.BLACK, self.button_create_prox_rect.inflate(
            2, 2), border_radius=20)
        pygame.draw.rect(self.screen, Color.GREEN,
                         self.button_create_prox_rect, border_radius=20)
        self.screen.blit(self.button_create_prox_text, self.button_create_prox_text.get_rect(
            center=self.button_create_prox_rect.center))
        self.screen.blit(self.button_back_text, self.button_back_text.get_rect(
            center=self.button_back_rect.center))

    def draw_rooms(self, total_pages):
        '''Desenha as salas em um carrossel (6 por página).'''
        if self.carousel_config['current_page'] != self.carousel_config['target_page']:
            direction = 1 if self.carousel_config['target_page'] > self.carousel_config['current_page'] else -1
            self.carousel_config['offset'] += direction * \
                self.carousel_config['animation_speed'] * Size.SCREEN_WIDTH
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
                x = self.rooms_start_x + \
                    (i % 3) * 220 + (page_offset * Size.SCREEN_WIDTH)
                y = self.rooms_start_y + (i // 3) * 100
                room_rect = pygame.Rect(x, y, 200, 80)
                self.elements_cur.append(('room', room_rect, room))
                pygame.draw.rect(self.screen, Color.WHITE,
                                 room_rect, border_radius=10)
                pygame.draw.rect(self.screen, Color.BLACK,
                                 room_rect, 2, border_radius=10)
                theme_text, _ = self.font_title_rooms.render(
                    room['name'].upper(), fgcolor=Color.DARK_GOLDEN)
                clients_text, _ = self.font_title_rooms.render(
                    f"{room['current_clients']}/{room['max_clients']}", fgcolor=Color.BLACK)
                info_surface = pygame.Surface(
                    (theme_text.get_width() + 10 + clients_text.get_width(),
                     max(theme_text.get_height(), clients_text.get_height())),
                    pygame.SRCALPHA
                )
                info_surface.blit(theme_text, (0, 0))
                info_surface.blit(
                    clients_text, (theme_text.get_width() + 10, 0))
                self.screen.blit(info_surface, info_surface.get_rect(
                    center=room_rect.center))
        if self.carousel_config['current_page'] > 0:
            self.elements_cur.append(('arrow_left', self.arrow_left_rect))
        if self.carousel_config['current_page'] < total_pages - 1:
            self.elements_cur.append(('arrow_right', self.arrow_right_rect))
        if self.carousel_config['current_page'] > 0:
            pygame.draw.polygon(self.screen, Color.BLACK, [
                (self.arrow_left_rect.left + 15, self.arrow_left_rect.centery),
                (self.arrow_left_rect.right, self.arrow_left_rect.top + 10),
                (self.arrow_left_rect.right, self.arrow_left_rect.bottom - 10)
            ])
        if self.carousel_config['current_page'] < total_pages - 1:
            pygame.draw.polygon(self.screen, Color.BLACK, [
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
        elif self.current_page == 'Play':
            if self.play_elements['button_leave'].collidepoint(self.mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            elif any(input.rect.collidepoint(self.mouse_pos) for input in [self.inputs[1], self.inputs[2]]):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return

    def handle_click_cursor(self):
        '''Verifica se o jogador clicou em algum elemento clicável.'''
        current_time = pygame.time.get_ticks()
        if current_time - self.last_click_time < 200:
            return
        mouse_click = pygame.mouse.get_pressed()[0]
        if not mouse_click:
            return
        self.last_click_time = current_time
        if self.current_page == 'Register':
            if (self.button_play_rect.collidepoint(self.mouse_pos) and self.inputs[0].text != '') or \
                    (self.inputs[0].return_pressed and self.inputs[0].text != ''):
                if len(self.inputs[0].text) > 7:
                    self.inputs[0].return_pressed = False
                    return
                self.name = self.inputs[0].text
                self.current_page = 'Rooms'
                super().start()
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                if self.current_input is not None:
                    self.current_input.active = False
                    self.current_input = None
        elif self.current_page == 'Rooms' and mouse_click:
            for element in self.elements_cur:
                elem_type, elem_rect = element[0], element[1]
                if elem_rect.collidepoint(self.mouse_pos):
                    if elem_type == 'room':
                        room = element[2]
                        password = None if room['type'] else ''
                        super().server_enter_room(room_code=room['code'], room_password=password)
                        self.current_page = 'Play'
                    elif elem_type == 'arrow_left':
                        self.carousel_config['target_page'] -= 1
                    elif elem_type == 'arrow_right':
                        self.carousel_config['target_page'] += 1
                    elif elem_type == 'button_create':
                        self.current_page = 'Create'
                        self.load_rooms = False
                    break
        elif self.current_page == 'Create' and mouse_click:
            if self.change_theme_button.collidepoint(self.mouse_pos):
                self.theme = random.choice(self.themes)
            elif self.button_create_prox_rect.collidepoint(self.mouse_pos):
                data_room = [input_field.text for input_field in self.inputs[3:5]]
                if all(data_room):
                    name, max_rounds = data_room
                    if max_rounds.isdigit() and 1 <= int(max_rounds) <= 20:
                        password = self.inputs[5].text
                        room_type = 'pub' if password == '' else 'priv'
                        if super().server_create_room(room_type, name, self.theme, str(max_rounds), password or None):
                            self.current_page = 'Play'
                            self.words = load_words(self.theme, int(max_rounds))
                            for input_field in self.inputs[3:5]:
                                input_field.text = ''
            elif self.button_back_rect.collidepoint(self.mouse_pos):
                self.current_page = 'Rooms'
                self.load_rooms = False
                for input_field in self.inputs[3:5]:
                    input_field.text = ''
        elif self.current_page == 'Play' and mouse_click:
            if self.play_elements['button_leave'].collidepoint(self.mouse_pos):
                if super().server_leave_room():
                    self.current_page = 'Rooms'
                    self.words = []
                    self.load_rooms = False
                    for client in self.room_clients.values(): # Reseta msgs
                        client['msgs'] = []
                    self.chat_all_scroll = 0

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
                "theme": data[3],
                "current_clients": data[4],
                "max_clients": data[5],
                "max_rounds": data[6]
            }
            self.rooms.append(room_data)

    def get_players(self):
        '''Carrega os jogadores da sala que o cliente está.'''
        ...

    def handle_chat(self, client=None, message=None):
        if self.inputs[2].return_pressed and self.inputs[2].text.strip() != '':
            mensagem = self.inputs[2].text.strip()[:12]
            super().client_chat(mensagem)
            with self.mutex:
                for client in self.room_clients.values():
                    if client['self']:
                        client['msgs'].append(mensagem)
            self.inputs[2].text = ''
            self.inputs[2].return_pressed = False
            self.inputs[2].active = False
            self.current_input = None
            self.chat_all_scroll = 0

    def handle_canvas(self, canvas):
        ...

    def handle_draw(self):
        ...
