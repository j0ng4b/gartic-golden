from game.screen.utils.utilities import *


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
    draw_rooms(self, total_pages)
    pygame.draw.rect(self.screen, Color.BLACK,
                     self.button_create_border, border_radius=20)
    pygame.draw.rect(self.screen, Color.GREEN,
                     self.button_create_rect, border_radius=20)
    self.screen.blit(self.button_create_text, self.button_create_text_rect)
    self.screen.blit(self.image_logo_big, self.image_logo_big_rect)
    self.screen.blit(self.available_rooms_text, self.available_rooms_pos)
    self.screen.blit(quant_rooms_surface, quant_rooms_rect)


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
