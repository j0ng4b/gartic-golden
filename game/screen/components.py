import pygame

from game.screen.utils.utilities import *


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


class Button(BaseComponent):
    def __init__(self, text, x, y, width, height, on_click=None, on_hover=None):
        self.text = text

        self.on_click = on_click
        self.on_hover = on_hover

        self.rect = pygame.Rect(x, y, width, height)

        self.button_surface = pygame.Surface((width, height))
        self.button_surface.fill(Color.GREEN)

        self.round_clip = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(self.round_clip, Color.WHITE, (0, 0, width, height), border_radius=20)

        self.font = None

    def init(self, surface, resource):
        super().init(surface, resource)

        self.font = resource.load_font('Acme-Regular', 30)
        self.update_text()

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if self.on_hover is not None:
                self.on_hover()

            if pygame.mouse.get_pressed()[0] and self.on_click is not None:
                self.on_click()

    def draw(self):
        self.surface.blit(self.button_surface, self.rect)

    def set_text(self, text):
        if self.text == text:
            return

        self.text = text
        self.update_text()

    def update_text(self):
        text_surface = self.font.render(self.text, True, Color.WHITE)
        text_rect = text_surface.get_rect()

        self.button_surface.fill(Color.GREEN)
        self.button_surface.blit(text_surface, [
            self.rect.width / 2 - text_rect.width / 2,
            self.rect.height / 2 - text_rect.height / 2
        ])

        self.button_surface.blit(self.round_clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
