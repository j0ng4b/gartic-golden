import pygame


class BaseComponent:
    def __init__(self):
        # Tela de desenho
        self.surface = None

        # Gerenciador de assets
        self.resource = None

    def init(self, surface, resource):
        '''
        Inicializa o componente
        --------------------

        Chamada para inicializar os elementos que estão no componente. Essa função
        deve ser chamada antes de usar o componente e deve ser chamada apenas uma vez.
        '''

        self.surface = surface
        self.resource = resource

    def update(self):
        '''
        Atualiza o componente
        --------------------

        Chamada para atualizar os elementos que estão no componente.
        '''
        pass

    def draw(self):
        '''
        Desenha o componente
        --------------------

        Chamada para desenhar os elementos que estão no componente.
        '''
        pass
