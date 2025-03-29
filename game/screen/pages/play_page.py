from game.screen.utils.utilities import *

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
    draw_card_players(self, scroll_area_players)
    self.inputs[1].draw(self.screen)
    self.inputs[2].draw(self.screen)
    draw_chat_all(self)
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
    '''Desenha os cards dos jogadores no painel.'''
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
    '''Desenha o chat geral.'''
    all_msgs = []
    for client in self.room_clients.values():
        for msg in client['msgs']:
            all_msgs.append({
                'text': msg[:12],
                'timestamp': int(msg[12:]),
                'sender': client['name'],
                'is_self': client['self']
            })
    all_msgs.sort(key=lambda x: x['timestamp'])
    total = len(all_msgs)
    self.scroll_max = max(0, total - 4)
    if total > 4:
        if self.chat_all_scroll == self.scroll_max:
            self.chat_all_scroll = total - 4 
    else:
        self.chat_all_scroll = 0
    pygame.draw.rect(self.screen, Color.LIGHT_GOLD, self.chat_all_rect, border_radius=5)
    old_clip = self.screen.get_clip()
    self.screen.set_clip(self.chat_all_rect)
    for i in range(4):
        idx = (total - 1) - (self.chat_all_scroll + i)
        if idx < 0 or idx >= total:
            continue
        msg = all_msgs[idx]
        prefix = "Você" if msg['is_self'] else msg['sender']
        color = Color.DARK_GREEN if msg['is_self'] else Color.BLACK
        text = f"{prefix}: {msg['text'].strip()}"
        surface = self.font_input_chat.render(text, True, color)
        y = self.chat_all_rect.bottom - 18 - (i * 18)  # Ajuste para exibir de baixo para cima
        x = self.chat_all_rect.right - 25 - surface.get_width() if msg['is_self'] else self.chat_all_rect.left + 25
        self.screen.blit(surface, (x, y))
    self.screen.set_clip(old_clip)

