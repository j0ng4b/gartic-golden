import abc

import pygame


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
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        for component in self.components:
            component.handle_input(event)

    @abc.abstractmethod
    def reset(self):
        '''
        Reseta a página
        --------------------

        Chamada para resetar os elementos que estão na página.
        '''
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
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

