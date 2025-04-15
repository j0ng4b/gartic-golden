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

        self.erasing = None
        self.drawing = None
        self.draw_points = []
        self.draw_points_time = 0
        self.draw_points_changed = True
        self.draw_points_send_interval = 0.5

    def init(self, client, surface, resource, goto_page):
        super().init(client, surface, resource, goto_page)

        self.add_components(
            components.Image(
                'logo_small',
                Size.SCREEN_WIDTH // 2 - 50,
                Size.SCREEN_HEIGHT // 2 - 250,
            ),

            # components.InputField(
            #     pygame.Rect(
            #         Size.SCREEN_WIDTH // 2 - 185,
            #         Size.SCREEN_HEIGHT - 45,
            #         250, 35
            #     ),

            #     'Mensagem...',
            #     on_enter=self.send_chat_message,
            # ),

            # components.InputField(
            #     pygame.Rect(
            #         Size.SCREEN_WIDTH // 2 + 95,
            #         Size.SCREEN_HEIGHT - 45,
            #         250, 35
            #     ),

            #     'Palpite...',
            #     on_enter=self.send_guess,
            # ),

            # components.Button(
            #     'Começar',
            #     20,
            #     Size.SCREEN_HEIGHT - 95,
            #     130, 35,
            #     on_click=self.start_game,
            # ),

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

        if self.client.state == 'draw' and self.draw_points_changed:
            current_time = pygame.time.get_ticks()
            if current_time - self.draw_points_time >= self.draw_points_send_interval:
                self.draw_points_time = current_time
                self.draw_points_changed = False
                self.client.client_canvas(self.draw_points)

    def draw(self):
        if self.surface is None:
            return
        super().draw()

        self.canvas.fill(Color.WHITE)
        for point in self.draw_points:
            pygame.draw.circle(self.canvas, Color.BLACK, point, 4)

        self.surface.blit(self.canvas, self.canvas_pos)

    def handle_input(self, event):
        if self.client is None:
            return
        super().handle_input(event)

        if self.client.state != 'draw':
            return

        # Desenhar com o botão esquerdo
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = (event.pos[0] - self.canvas_pos[0], event.pos[1] - self.canvas_pos[1])
            if self.canvas.get_rect().collidepoint(pos):
                self.drawing = pos

                # Adiciona o ponto à lista de pontos desenhados
                self.draw_points.append(pos)
                self.draw_points_time = pygame.time.get_ticks()
                self.draw_points_changed = True

        # Iniciar apagamento com o botão direito
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            pos = (event.pos[0] - self.canvas_pos[0], event.pos[1] - self.canvas_pos[1])
            if self.canvas.get_rect().collidepoint(pos):
                self.erasing = pos
                self.erase_points_at_position(pos)
                self.draw_points_time = pygame.time.get_ticks()
                self.draw_points_changed = True

        # Movimento do mouse
        elif event.type == pygame.MOUSEMOTION:
            pos = (event.pos[0] - self.canvas_pos[0], event.pos[1] - self.canvas_pos[1])
            
            # Continuar desenhando se o botão esquerdo estiver pressionado
            if self.drawing is not None and self.canvas.get_rect().collidepoint(pos):
                self.drawing = pos
                # Adiciona o ponto à lista de pontos desenhados
                self.draw_points.append(pos)
                self.draw_points_time = pygame.time.get_ticks()
                self.draw_points_changed = True
                
            # Continuar apagando se o botão direito estiver pressionado
            if self.erasing is not None and self.canvas.get_rect().collidepoint(pos):
                self.erasing = pos
                self.erase_points_at_position(pos)
                self.draw_points_time = pygame.time.get_ticks()
                self.draw_points_changed = True

        # Finalizar desenho ou apagamento
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.drawing = None
            elif event.button == 3:
                self.erasing = None

    def reset(self):
        super().reset()
        self.draw_points.clear()

    def handle_canvas(self, canvas_data):
        if self.client is None or self.client.state == 'draw':
            return

        self.draw_points = canvas_data

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

    def start_game(self):
        if self.client is None:
            return

        self.client.server_close_room()

    def quit_room(self):
        if self.client is None or self.goto_page is None:
            return

        # Envia a mensagem de saída para o servidor
        self.client.server_leave_room()

        # Retorna para a tela inicial
        self.goto_page('rooms')

    def erase_points_at_position(self, pos, radius=10):
        """
        Apaga pontos próximos à posição fornecida.

        Args:
            pos (tuple): Posição (x, y) onde ocorreu o clique
            radius (int): Raio da área de apagamento
        """
        points_to_keep = []
        for point in self.draw_points:
            # Calcula a distância entre o ponto e a posição do clique
            distance = ((point[0] - pos[0]) ** 2 + (point[1] - pos[1]) ** 2) ** 0.5
            # Mantém apenas os pontos que estão fora do raio de apagamento
            if distance > radius:
                points_to_keep.append(point)

        # Atualiza a lista de pontos
        if len(points_to_keep) < len(self.draw_points):
            self.draw_points = points_to_keep
            self.draw_points_changed = True

