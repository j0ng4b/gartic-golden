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
        if input_value is None:
            input_value = self.components[2].get_text()

        # Define o nome do cliente para o valor do input
        self.client.name = input_value

        # Executa o comando de registro no servidor e outras mágicas da classe
        # BaseClient
        BaseClient.start(self.client)

        self.goto_page('rooms')


class RoomsPage(BasePage):
    def __init__(self):
        super().__init__()

        self.rooms = []

        # Tempo para atualizar a lista de salas automaticamente
        self.auto_list_time = 0
        self.auto_list_interval = 1500

    def init(self, client, surface, resource, goto_page):
        super().init(client, surface, resource, goto_page)

        self.add_components(
            components.Image(
                'logo',
                Size.SCREEN_WIDTH // 2,
                Size.SCREEN_HEIGHT // 2 - 200,
            ),

            components.Label(
                'Salas disponíveis',
                Size.SCREEN_WIDTH // 2,
                Size.SCREEN_HEIGHT // 2 - 110,
            ),

            components.Button(
                'Criar sala',
                Size.SCREEN_WIDTH // 2 - 94,
                Size.SCREEN_HEIGHT // 2 + 210,
                185,
                50,

                on_click=self.create_room_button_click,
            ),
        )

    def update(self):
        super().update()

        # Atualiza a lista de salas automaticamente
        current_time = pygame.time.get_ticks()
        if current_time - self.auto_list_time > self.auto_list_interval:
            self.update_rooms_list()
            self.auto_list_time = current_time

    def draw(self):
        super().draw()

        # TODO: Desenhar a lista de salas

    def handle_input(self, event):
        super().handle_input(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # TODO: Lidar com o clique em uma sala
            pass

    def reset(self):
        super().reset()

    def create_room_button_click(self):
        self.goto_page('create_room')

    def update_rooms_list(self):
        rooms = self.client.server_list_rooms()
        if len(rooms) == 1 and rooms[0] == '':
            return

        self.rooms.clear()
        for room in rooms:
            data = room.strip().split(",")
            self.rooms.append({
                "type": data[0],
                "name": data[1],
                "code": data[2],
                "num_clients": data[3],
                "max_clients": data[4]
            })


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
        )

    def update(self):
        super().update()

    def draw(self):
        if self.surface is None:
            return
        super().draw()

        self.surface.blit(self.canvas, self.canvas_pos)

    def handle_input(self, event):
        super().handle_input(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = (event.pos[0] - self.canvas_pos[0], event.pos[1] - self.canvas_pos[1])
            if self.inside_round_rect(*pos):
                self.drawing = pos
        elif event.type == pygame.MOUSEMOTION:
            pos = (event.pos[0] - self.canvas_pos[0], event.pos[1] - self.canvas_pos[1])
            if self.drawing is not None and self.inside_round_rect(*pos):
                pygame.draw.circle(self.canvas, Color.BLACK, self.drawing, 4)
                self.drawing = pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drawing = None

    def reset(self):
        super().reset()

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

