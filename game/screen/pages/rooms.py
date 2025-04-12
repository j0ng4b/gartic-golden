import pygame

from game.screen import components
from game.screen.pages.base import BasePage
from game.screen.constants import Color, Size


class RoomsPage(BasePage):
    def __init__(self):
        super().__init__()

        self.rooms = []
        self.room_start_pos = (
            Size.SCREEN_WIDTH // 2 - 330,
            Size.SCREEN_HEIGHT // 2 - 30
        )
        self.room_rect = pygame.Rect(0, 0, 200, 80)

        self.font = None

        # Tempo para atualizar a lista de salas automaticamente
        self.auto_list_time = 0
        self.auto_list_interval = 1500

    def init(self, client, surface, resource, goto_page):
        super().init(client, surface, resource, goto_page)

        self.font = resource.load_font('Acme-Regular', 19)

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

        # Verifica se o mouse está sobre uma sala
        for i in range(len(self.rooms)):
            room_rect = self.room_rect.move(
                self.room_start_pos[0] + (i % 3) * 220,
                self.room_start_pos[1] + (i // 3) * 100
            )

            if room_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def draw(self):
        if self.surface is None or self.font is None:
            return
        super().draw()

        for i in range(len(self.rooms)):
            room = self.rooms[i]

            room_rect = self.room_rect.move(
                self.room_start_pos[0] + (i % 3) * 220,
                self.room_start_pos[1] + (i // 3) * 100
            )
            pygame.draw.rect(self.surface, Color.WHITE, room_rect, border_radius=10)

            # Desenha o texto da sala
            text = f"{room['name']} ({room['num_clients']}/{room['max_clients']})"
            text_surface = self.font.render(text, True, Color.BLACK)
            text_rect = text_surface.get_rect(center=room_rect.center)
            self.surface.blit(text_surface, text_rect)

    def handle_input(self, event):
        super().handle_input(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.rooms)):
                room_rect = self.room_rect.move(
                    self.room_start_pos[0] + (i % 3) * 220,
                    self.room_start_pos[1] + (i // 3) * 100
                )

                if not room_rect.collidepoint(pygame.mouse.get_pos()):
                    continue

                # TODO: implementar a lógica de entrar na sala

    def reset(self):
        super().reset()

    def create_room_button_click(self):
        self.goto_page('create_room')

    def update_rooms_list(self):
        self.rooms.clear()

        rooms = self.client.server_list_rooms()
        if len(rooms) == 1 and rooms[0] == '':
            return

        self.rooms.clear()
        for room in rooms:
            if room == '':
                continue

            data = room.strip().split(',')
            self.rooms.append({
                'type': data[0],
                'name': data[1],
                'code': data[2],
                'theme': data[3],
                'num_clients': data[4],
                'max_clients': data[5]
            })

