import pygame

from game.screen import components
from game.screen.constants import Size
from game.screen.pages.base import BasePage


class CreateRoomPage(BasePage):
    def __init__(self):
        super().__init__()

    def init(self, client, surface, resource, goto_page):
        super().init(client, surface, resource, goto_page)

        self.add_components(
            components.Image(
                'logo',
                Size.SCREEN_WIDTH // 2,
                Size.SCREEN_HEIGHT // 2 - 200,
            ),

            components.InputField(
                pygame.Rect(
                    Size.SCREEN_WIDTH // 2 - 315,
                    Size.SCREEN_HEIGHT // 2 - 50,
                    270, 40
                ),

                'Nome da sala',
                on_enter=(lambda _: self.focus_next(0))
            ),

            components.InputField(
                pygame.Rect(
                    Size.SCREEN_WIDTH // 2 + 45,
                    Size.SCREEN_HEIGHT // 2 - 50,
                    270, 40
                ),

                'Senha da sala',
                on_enter=(lambda _: self.focus_next(1))
            ),

            components.InputField(
                pygame.Rect(
                    Size.SCREEN_WIDTH // 2 - 135,
                    Size.SCREEN_HEIGHT // 2 + 50,
                    270, 40
                ),

                'Tema da sala',
                on_enter=self.create_room,
            ),

            components.Button(
                'Voltar',
                Size.SCREEN_WIDTH // 2 - 300,
                Size.SCREEN_HEIGHT - 100,
                200, 50,

                on_click=(lambda: self.goto_page('rooms'))
            ),

            components.Button(
                'Criar',
                Size.SCREEN_WIDTH // 2 + 100,
                Size.SCREEN_HEIGHT - 100,
                200, 50,
                on_click=self.create_room,
            ),
        )

    def update(self):
        super().update()

    def draw(self):
        super().draw()

    def handle_input(self, event):
        super().handle_input(event)

    def reset(self):
        super().reset()

        self.components[1].set_text('')
        self.components[2].set_text('')
        self.components[3].set_text('')

    def create_room(self, room_theme=None):
        room_type = 'priv'
        room_name = self.components[1].get_text()
        room_password = self.components[2].get_text()
        if room_password == '':
            room_type = 'pub'
            room_password = None

        if room_theme is None:
            room_theme = self.components[3].get_text()

        if self.client.server_create_room(room_type, room_name, room_theme, room_password):
            self.client.state = 'draw'
            self.goto_page('play')

    def focus_next(self, cur_input):
        self.components[cur_input + 1].active = False
        self.components[cur_input + 2].active = True

