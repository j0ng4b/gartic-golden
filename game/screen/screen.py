import pygame
import os

import pygame.freetype
from game.client.base import BaseClient
from .utils.utilities import *


class InputField():
    def __init__(self, rect: pygame.rect, font: pygame.font.Font, placeholder=''):
        self.rect = rect
        self.font = font
        self.text = ''
        self.active = False
        self.placeholder = placeholder
        self.return_pressed = False
        self.text_offset = 0
        self.padding = 6
        self.cursor_width = 2
        self.cursor_pos = 0
        self.cursor_visible = True
        self.cursor_interval = 500
        self.time = pygame.time.get_ticks()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.time = pygame.time.get_ticks()
            self.cursor_visible = True

        if self.active and event.type == pygame.KEYDOWN:
            self.time = pygame.time.get_ticks()
            self.cursor_visible = True
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0 and len(self.text) > 0:
                    self.text = self.text[:self.cursor_pos -
                                          1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE and self.cursor_pos < len(self.text):
                self.text = self.text[:self.cursor_pos] + \
                    self.text[self.cursor_pos+1:]
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif event.key == pygame.K_RETURN:
                if self.text:
                    self.return_pressed = True
            else:
                self.text = self.text[:self.cursor_pos] + \
                    event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1
            self.update_text_offset()

    def update_text_offset(self):
        max_width = self.rect.width - 2 * self.padding
        cursor_pixel_pos = self.font.size(self.text[:self.cursor_pos])[0]
        text_width = self.font.size(self.text)[0]
        self.text_offset = max(
            0, min(cursor_pixel_pos, text_width - max_width, cursor_pixel_pos - max_width))

    def draw(self, screen):
        pygame.draw.rect(screen, Color.WHITE, self.rect, border_radius=8)
        pygame.draw.rect(screen, Color.BLACK, self.rect, 2, border_radius=8)

        display_text = self.text if self.text else self.placeholder
        text_color = Color.BLACK if self.text else Color.LIGHT_GRAY
        text = self.font.render(display_text, True, text_color)
        text_clip_rect = pygame.Rect(
            self.rect.x + self.padding,
            self.rect.y + self.padding,
            self.rect.width - 2 * self.padding,
            self.rect.height - 2 * self.padding
        )
        old_clip = screen.get_clip()
        screen.set_clip(text_clip_rect)
        text_rect = text.get_rect(
            midleft=(self.rect.x + self.padding - self.text_offset,
                     self.rect.y + self.rect.height // 2))
        screen.blit(text, text_rect)
        screen.set_clip(old_clip)

        current_time = pygame.time.get_ticks()
        if current_time - self.time > self.cursor_interval:
            self.cursor_visible = not self.cursor_visible
            self.time = current_time
        if self.active and self.cursor_visible:
            cursor_pixel_pos = self.font.size(self.text[:self.cursor_pos])[0]
            cursor_x = self.rect.x + self.padding + cursor_pixel_pos - self.text_offset
            cursor_x = max(self.rect.x + self.padding,
                           min(cursor_x, self.rect.x + self.rect.width - self.padding))
            cursor_top = self.rect.y + self.padding
            cursor_height = self.rect.height - 2 * self.padding
            pygame.draw.line(
                screen, (0, 0, 0),
                (cursor_x, cursor_top),
                (cursor_x, cursor_top + cursor_height),
                self.cursor_width
            )


class Screen(BaseClient):
    def __init__(self, address, port):
        super().__init__(address, port)
        pygame.init()
        pygame.freetype.init()
        base_path = os.path.dirname(__file__)

        # Janela
        pygame.display.set_icon(pygame.image.load(os.path.join(
            os.path.dirname(__file__), 'assets', 'ico.png')))
        pygame.display.set_caption('Gartic Golden')
        self.screen = pygame.display.set_mode(
            (Size.SCREEN_WIDTH, Size.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Fontes
        self.font_label = pygame.font.Font(os.path.join(
            base_path, 'font', 'Acme-Regular.ttf'), 40)
        self.font_button = pygame.font.Font(os.path.join(
            base_path, 'font', 'Acme-Regular.ttf'), 30)
        self.font_input_name = pygame.font.Font(
            os.path.join(base_path, 'font', 'Acme-Regular.ttf'), 26)
        self.font_title_rooms = pygame.freetype.Font(
            os.path.join(base_path, 'font', 'Acme-Regular.ttf'), 19)
        self.font_title_rooms.strong = True
        self.font_input_chat = pygame.font.Font(
            os.path.join(base_path, 'font', 'Acme-Regular.ttf'), 18)

        # Imagens
        self.image_logo = pygame.image.load(
            os.path.join(base_path, 'assets', 'logo.png'))
        self.image_logo_small = pygame.image.load(
            os.path.join(base_path, 'assets', 'logo_small.png'))
        self.icon_user = pygame.image.load(
            os.path.join(base_path, 'assets', 'user.png'))
        self.user_icon = pygame.transform.scale(self.icon_user, (30, 30))
        self.pencil = pygame.image.load(
            os.path.join(base_path, 'assets', 'pencil.png'))
        self.pencil_icon = pygame.transform.scale(self.pencil, (20, 20))

        # Estado do jogo
        self.running = True
        self.current_page = 'Register'  # Página inicial - 'Register'
        self.current_input = None

        # Configs
        self.carousel_config = {
            'current_page': 0, 'target_page': 0, 'offset': 0, 'animation_speed': 0.1}

        # Painel lateral de jogadores
        self.left_panel = pygame.Rect(
            0, 50, Size.SCREEN_WIDTH // 5 - 5, Size.SCREEN_HEIGHT)

        # Campos de entrada
        self.inputs = [
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 - 150, Size.SCREEN_HEIGHT // 2, 300, 40),
                       self.font_input_name, "Digite seu nick"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 - 185, Size.SCREEN_HEIGHT - 85, 250, 35),
                       self.font_input_chat, "Digite sua resposta"),
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 + 95, Size.SCREEN_HEIGHT - 85, 250, 35),
                       self.font_input_chat, "Converse no Chat")
        ]

        self.players = []
        self.rooms = []

    def start(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
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
        elif self.current_page == 'Create Room':
            self.create_room_page()
        elif self.current_page == 'Play':
            self.play_page()
        elif self.current_page == 'Test':
            self.play_page()

    def register_page(self):
        prox_page = False

        image_rect = self.image_logo.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 200))

        text = self.font_label.render('DIGITE SEU NICK', True, Color.BLACK)
        text_rect = text.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 50))

        self.inputs[0].draw(self.screen)

        button = pygame.Rect(Size.SCREEN_WIDTH // 2 - 100,
                             Size.SCREEN_HEIGHT // 2 + 100, 200, 50)
        pygame.draw.rect(self.screen, Color.BLACK,
                         button.inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.screen, Color.GREEN, button, border_radius=20)
        button_text = self.font_button.render('JOGAR', True, Color.WHITE)
        button_text_rect = button_text.get_rect(center=button.center)

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        # Cursor diferente para o mouse colidindo com o botão ou input
        if button.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.inputs[0].rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Casos para ir para próxima página
        if button.collidepoint(mouse_pos) and mouse_click[0] and self.inputs[0].text != '':
            prox_page = True
        elif self.inputs[0].return_pressed and self.inputs[0].text != '':
            prox_page = True

        self.screen.blit(text, text_rect)
        self.screen.blit(self.image_logo, image_rect)
        self.screen.blit(button_text, button_text_rect)

        if prox_page:
            self.name = self.inputs[0].text
            super().start()
            self.current_page = ''  # Colocar próxima página que seria a de salas
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            if self.current_input is not None:
                self.current_input.active = False
                self.current_input = None

    def rooms_page(self):
        # Aqui onde eu preparo as salas
        # Uma lista de salas, com chaves como 'theme', 'password', 'max_clients' e 'room_code'
        self.rooms = []

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
                    room['theme'], fgcolor=Color.DARK_GOLDEN)
                max_clients, _ = self.font_title_rooms.render(
                    room['max_clients'], fgcolor=Color.BLACK)
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
            Size.SCREEN_WIDTH // 2 - 114, Size.SCREEN_HEIGHT // 2 + 210, 220, 50)
        pygame.draw.rect(self.screen, Color.BLACK,
                         button_create.inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.screen, Color.GREEN,
                         button_create, border_radius=20)
        button_text = self.font_button.render('CRIAR SALA', True, Color.WHITE)
        self.screen.blit(button_text, button_text.get_rect(
            center=button_create.center))
        self.screen.blit(self.image_logo, self.image_logo.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 200)))
        self.screen.blit(self.font_label.render('SALAS DISPONÍVEIS', True, Color.BLACK),
                         (Size.SCREEN_WIDTH // 2 - 150, Size.SCREEN_HEIGHT // 2 - 110))
        
        if button_create.collidepoint(mouse_pos) and mouse_click[0]: 
            self.current_page = 'Create Room'

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

    def create_room_page():
        ...

    def handle_chat(self, client, message):
        print(f'~{client["name"]}: {message}')

    def handle_canvas(self, canvas):
        print(f'canvas: {canvas}')


if __name__ == '__main__':
    Screen('gg.nengue.xyz', 2611).start()
