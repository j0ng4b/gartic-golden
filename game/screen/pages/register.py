import pygame

from game.screen import components
from game.client.base import BaseClient
from game.screen.pages.base import BasePage
from game.screen.constants import Size


class RegisterPage(BasePage):
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

            components.Label(
                'Digite seu nick:',
                Size.SCREEN_WIDTH // 2,
                Size.SCREEN_HEIGHT // 2 - 50,
            ),

            components.InputField(
                pygame.Rect(
                    Size.SCREEN_WIDTH // 2 - 150,
                    Size.SCREEN_HEIGHT // 2,
                    300,
                    40
                ),

                'elPabloPicasso',
                on_enter=self.play_button_click,
            ),

            components.Button(
                'Jogar',
                Size.SCREEN_WIDTH // 2 - 100,
                Size.SCREEN_HEIGHT // 2 + 100,
                200,
                50,

                on_click=self.play_button_click,
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

    def play_button_click(self, input_value=None):
        if self.client is None or self.goto_page is None:
            return

        if input_value is None:
            input_value = self.components[2].get_text()

        # Define o nome do cliente para o valor do input
        self.client.name = input_value

        # Executa o comando de registro no servidor e outras mágicas da classe
        # BaseClient
        BaseClient.start(self.client)

        self.goto_page('rooms')

