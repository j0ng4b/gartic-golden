import pygame

from game.screen import components
from game.screen.pages.base import BasePage
from game.screen.constants import Color, Size


class PlayPage(BasePage):
    BORDER_RADIUS = 20
    CANVAS_WIDTH = Size.SCREEN_WIDTH - 175
    CANVAS_HEIGHT = Size.SCREEN_HEIGHT // 2 + 30


    def __init__(self):
        super().__init__()

        self.canvas_pos = (Size.SCREEN_WIDTH // 4 - 40, Size.SCREEN_HEIGHT // 4 - 55)
        self.canvas = pygame.Surface((self.CANVAS_WIDTH, self.CANVAS_HEIGHT), pygame.SRCALPHA)
        self.canvas.fill(Color.WHITE)

        self.round_clip = pygame.Surface((self.CANVAS_WIDTH, self.CANVAS_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.round_clip, Color.WHITE,
                         (0, 0, self.CANVAS_WIDTH, self.CANVAS_HEIGHT),
                         border_radius=self.BORDER_RADIUS)

        self.canvas.blit(self.round_clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        self.drawing = None

    def init(self, client, surface, resource, goto_page):
        super().init(client, surface, resource, goto_page)

        self.add_components(
            components.Image(
                'logo_small',
                Size.SCREEN_WIDTH // 2 - 50,
                Size.SCREEN_HEIGHT // 2 - 250,
            ),

            components.InputField(
                pygame.Rect(
                    Size.SCREEN_WIDTH // 2 - 185,
                    Size.SCREEN_HEIGHT - 45,
                    250, 35
                ),

                'Mensagem...',
                on_enter=self.send_chat_message,
            ),

            components.InputField(
                pygame.Rect(
                    Size.SCREEN_WIDTH // 2 + 95,
                    Size.SCREEN_HEIGHT - 45,
                    250, 35
                ),

                'Palpite...',
                on_enter=self.send_guess,
            ),

            components.Button(
                'Sair',
                35,
                Size.SCREEN_HEIGHT - 45,
                100, 35,
                on_click=self.quit_room,
            ),
        )

    def update(self):
        if self.client is None:
            return
        super().update()

        if self.client.state == 'draw':
            canvas_data = pygame.surfarray.array3d(self.canvas)
            self.client.client_canvas(canvas_data)

    def draw(self):
        if self.surface is None:
            return
        super().draw()

        self.surface.blit(self.canvas, self.canvas_pos)

    def handle_input(self, event):
        if self.client is None:
            return
        super().handle_input(event)

        if self.client.state != 'draw':
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = (event.pos[0] - self.canvas_pos[0], event.pos[1] - self.canvas_pos[1])
            if self.canvas.get_rect().collidepoint(pos) and self.inside_round_rect(*pos):
                pygame.draw.circle(self.canvas, Color.BLACK, pos, 4)
                self.drawing = pos
        elif event.type == pygame.MOUSEMOTION:
            if self.drawing is None:
                return

            pos = (event.pos[0] - self.canvas_pos[0], event.pos[1] - self.canvas_pos[1])
            if self.canvas.get_rect().collidepoint(pos) and self.inside_round_rect(*pos):
                pygame.draw.circle(self.canvas, Color.BLACK, pos, 4)
                self.drawing = pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drawing = None

    def reset(self):
        super().reset()

    def send_chat_message(self, input_value=None):
        if self.client is None:
            return

        if input_value is None:
            input_value = self.components[1].get_text()

        # Limpa o campo de texto
        self.components[1].set_text('')

        # Envia a mensagem para o servidor
        self.client.client_chat(input_value)

    def send_guess(self, input_value=None):
        if self.client is None:
            return

        if input_value is None:
            input_value = self.components[2].get_text()

        # Limpa o campo de texto
        self.components[2].set_text('')

        # Envia o palpite para o servidor
        self.client.client_guess(input_value)

    def quit_room(self):
        if self.client is None:
            return

        # Envia a mensagem de saída para o servidor
        self.client.server_leave_room()

        # Retorna para a tela inicial
        self.goto_page('rooms')

    def inside_round_rect(self, x, y):
        r = self.BORDER_RADIUS
        w = self.CANVAS_WIDTH
        h = self.CANVAS_HEIGHT

        if x < r and y < r:
            return (x - r)**2 + (y - r)**2 <= r*r
        elif x > w - r and y < r:
            return (x - (w - r))**2 + (y - r)**2 <= r*r
        elif x < r and y > h - r:
            return (x - r)**2 + (y - (h - r))**2 <= r*r
        elif x > w - r and y > h - r:
            return (x - (w - r))**2 + (y - (h - r))**2 <= r*r
        else:
            return True

