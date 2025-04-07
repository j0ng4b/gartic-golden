import abc

import pygame

import game.screen.components as components
from game.client.base import BaseClient
from game.screen.utils.utilities import *


class BasePage(abc.ABC):
    def __init__(self):
        # Tela de desenho
        self.surface = None

        # Gerenciador de assets
        self.resource = None

        # Utiliza o goto_page para ir para outra página
        # quando necessário
        self.goto_page = None

        # Cliente usando para comunicar com o servidor
        self.client = None

        # Lista de componentes que estão na página
        # Exemplo: botoes, textos, imagens
        self.components = []

    @abc.abstractmethod
    def init(self, client, surface, resource, goto_page):
        '''
        Inicializa a página
        --------------------

        Chamada para inicializar os elementos que estão na página. Essa função
        deve ser chamada antes de usar a página e deve ser chamada apenas uma vez.
        '''

        self.client = client
        self.surface = surface
        self.resource = resource
        self.goto_page = goto_page

    @abc.abstractmethod
    def update(self):
        '''
        Atualiza a página
        --------------------

        Chamada para atualizar os elementos que estão na página.
        '''
        for component in self.components:
            component.update()

    @abc.abstractmethod
    def draw(self):
        '''
        Desenha a página
        --------------------

        Chamada para desenhar os elementos que estão na página.
        '''
        for component in self.components:
            component.draw()

    @abc.abstractmethod
    def handle_input(self, event):
        '''
        Lida com a entrada do usuário
        --------------------

        Chamada para lidar com a entrada do usuário na página.
        '''
        for component in self.components:
            component.handle_input(event)

    @abc.abstractmethod
    def reset(self):
        '''
        Reseta a página
        --------------------

        Chamada para resetar os elementos que estão na página.
        '''
        pass

    def add_components(self, *components):
        '''
        Adiciona um componente à página
        --------------------

        Chamada para adicionar um componente à página.
        '''
        for component in components:
            component.init(self.surface, self.resource)
            self.components.append(component)


class RegisterPage(BasePage):
    def __init__(self):
        super().__init__()

    def init(self, client, surface, resource, goto_page):
        super().init(client, surface, resource, goto_page)

        self.add_components(
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
        pass

    def play_button_click(self, input_value=None):
        if input_value is None:
            input_value = self.components[0].get_value()

        # Define o nome do cliente para o valor do input
        self.client.name = input_value

        # Executa o comando de registro no servidor e outras mágicas da classe
        # BaseClient
        BaseClient.start(self.client)

        self.goto_page('rooms')

