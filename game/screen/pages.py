import abc

import pygame

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

        # Lista de componentes que estão na página
        # Exemplo: botoes, textos, imagens
        self.components = []

    @abc.abstractmethod
    def init(self, surface, resource, goto_page):
        '''
        Inicializa a página
        --------------------

        Chamada para inicializar os elementos que estão na página. Essa função
        deve ser chamada antes de usar a página e deve ser chamada apenas uma vez.
        '''

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

    def add_component(self, component):
        '''
        Adiciona um componente à página
        --------------------

        Chamada para adicionar um componente à página.
        '''
        self.components.append(component)
        component.init(self.surface, self.resource)


class RegisterPage(BasePage):
    def __init__(self):
        super().__init__()

    def init(self, surface, resource, goto_page):
        super().init(surface, resource, goto_page)
        pass

    def update(self):
        super().update()

    def draw(self):
        super().draw()

    def handle_input(self, event):
        super().handle_input(event)

    def reset(self):
        pass
