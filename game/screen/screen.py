import pygame

from game.client.base import BaseClient
from game.screen.pages.base import BasePage
from game.screen.resource import Resource
from game.screen.utils.utilities import *


class Screen(BaseClient):
    def __init__(self, address, port):
        super().__init__(address, port)

        # Armazenar as "páginas" (telas) do jogo
        self.pages = {}
        self.current_page = None

        # Gerenciador de assets
        self.resource = Resource()

        pygame.init()

        # Janela
        path = os.path.dirname(__file__)
        pygame.display.set_icon(pygame.image.load(os.path.join(path, 'assets', 'images', 'ico.png')))
        pygame.display.set_caption('Gartic Golden')

        self.surface = pygame.display.set_mode((Size.SCREEN_WIDTH, Size.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.running = False

    def register_page(self, page_name, page):
        if isinstance(page, BasePage) and page_name not in self.pages:
            self.pages[page_name] = page

            # Inicializa a página com o método init
            page.init(self, self.surface, self.resource, self.goto_page)

    def goto_page(self, page_name):
        if page_name in self.pages:
            self.current_page = self.pages[page_name]

            # Toda vez que a página é alterada a nova página é resetada
            self.current_page.reset()

    def start(self):
        if self.current_page is None:
            raise Exception('Uma tela defe ser especificada')

        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.handle_close_game()
                else:
                    self.current_page.handle_input(event)

            # Atualiza a página atual
            self.current_page.update()

            # Desenha a página atual
            self.surface.fill(Color.GOLDEN)
            self.current_page.draw()
            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

    def handle_close_game(self):
        self.running = False

        if self.room:
            super().server_leave_room()

        if self.current_page != self.pages['register']:
            super().server_unregister()

    def handle_chat(self, client, message):
        if self.current_page is None:
            return

        if hasattr(self.current_page, 'handle_chat'):
            self.current_page.handle_chat(client, message)

    def handle_canvas(self, canvas):
        if self.current_page is None:
            return

        if hasattr(self.current_page, 'handle_canvas'):
            self.current_page.handle_canvas(canvas)

    def initiate_drawing(self):
        if self.current_page is None:
            return

        if hasattr(self.current_page, 'handle_draw'):
            self.current_page.handle_draw()

