import pygame
import os
from game.client.base import BaseClient
from .utils.utilities import *


class InputField():
    def __init__(self, rect, font, placeholder=''):
        self.rect = rect
        self.font = font
        self.text = ''
        self.active = False
        self.placeholder = placeholder
        self.return_pressed = False
        self.text_offset = 0
        self.padding = 6
        self.cursor_width = 2
        self.cursor_pos = 0
        self.cursor_visible = True
        self.cursor_interval = 500
        self.time = pygame.time.get_ticks()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.time = pygame.time.get_ticks()
            self.cursor_visible = True
        
        if self.active:
            if event.type == pygame.KEYDOWN:
                self.time = pygame.time.get_ticks()
                self.cursor_visible = True
                if event.key == pygame.K_BACKSPACE and self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                elif event.key == pygame.K_DELETE and self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
                elif event.key == pygame.K_LEFT:
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                elif event.key == pygame.K_RIGHT:
                    self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
                elif event.key == pygame.K_HOME:
                    self.cursor_pos = 0
                elif event.key == pygame.K_END:
                    self.cursor_pos = len(self.text)
                elif event.key == pygame.K_RETURN:
                    self.return_pressed = True
                else:
                    self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                    self.cursor_pos += 1
                self.update_text_offset()

    def update_text_offset(self):
        max_width = self.rect.width - 2 * self.padding
        cursor_pixel_pos = self.font.size(self.text[:self.cursor_pos])[0]
        text_width = self.font.size(self.text)[0]
        self.text_offset = max(0, min(cursor_pixel_pos, text_width - max_width, cursor_pixel_pos - max_width))

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=8)
        display_text = self.text if self.text else self.placeholder
        text_color = (0, 0, 0) if self.text else (169, 169, 169)
        text = self.font.render(display_text, True, text_color)

        text_clip_rect = pygame.Rect(
            self.rect.x + self.padding,
            self.rect.y + self.padding,
            self.rect.width - 2 * self.padding,
            self.rect.height - 2 * self.padding
        )

        old_clip = screen.get_clip()
        screen.set_clip(text_clip_rect)
        text_rect = text.get_rect(
            midleft=(self.rect.x + self.padding - self.text_offset, 
                    self.rect.y + self.rect.height // 2))
        screen.blit(text, text_rect)

        screen.set_clip(old_clip)
        current_time = pygame.time.get_ticks()
        if current_time - self.time > self.cursor_interval:
            self.cursor_visible = not self.cursor_visible
            self.time = current_time
        if self.active and self.cursor_visible:
            cursor_pixel_pos = self.font.size(self.text[:self.cursor_pos])[0]
            cursor_x = self.rect.x + self.padding + cursor_pixel_pos - self.text_offset
            cursor_x = max(self.rect.x + self.padding,
                        min(cursor_x, self.rect.x + self.rect.width - self.padding))
            cursor_top = self.rect.y + self.padding
            cursor_height = self.rect.height - 2 * self.padding
            pygame.draw.line(
                screen, (0, 0, 0),
                (cursor_x, cursor_top),
                (cursor_x, cursor_top + cursor_height),
                self.cursor_width
            )


class Screen(BaseClient):
    def __init__(self, address, port):
        super().__init__(address, port)
        pygame.init()
        pygame.display.set_icon(pygame.image.load(os.path.join(
            os.path.dirname(__file__), 'assets', 'ico.png')))
        pygame.display.set_caption('Gartic Golden')

        self.screen = pygame.display.set_mode(
            (Size.SCREEN_WIDTH, Size.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_label = pygame.font.Font(os.path.join(
            os.path.dirname(__file__), 'font', 'Acme-Regular.ttf'), 40)
        self.font_input_name = pygame.font.Font(os.path.join(
            os.path.dirname(__file__), 'font', 'Acme-Regular.ttf'), 26)
        self.running = True

        # Controlador - Page
        self.current_page = 'Register'  # Primeira página para registrar o nome
        self.button_jogar = False

        # Lista de inputs
        self.inputs = [
            InputField(pygame.Rect(Size.SCREEN_WIDTH // 2 - 150, Size.SCREEN_HEIGHT //
                       2, 300, 40), self.font_input_name, "Digite seu nick"),
        ]
        self.current_input = None

    def start(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Caso clicar em algum campo de entrada
                    self.current_input = None
                    for input_field in self.inputs:
                        if input_field.rect.collidepoint(event.pos):
                            input_field.active = True
                            self.current_input = input_field
                            break
                        else:
                            input_field.active = False

                if self.current_input is not None:
                    self.current_input.handle_event(event)

            self.screen.fill(Color.GOLDEN)
            self.draw_page()
            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

    def draw_page(self):
        if self.current_page == 'Register':
            self.register_page()
        elif self.current_page == 'Rooms':
            ...
        elif self.current_page == 'Create Room':
            ...
        elif self.current_page == 'Play':
            ...
        elif self.current_page == 'Teste':
            self.test_page()

    def register_page(self):
        prox_page = False
        # Logo
        image_logo = pygame.image.load(os.path.join(
            os.path.dirname(__file__), 'assets', 'logo.png'))
        image_rect = image_logo.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 200))
        # Label
        text = self.font_label.render('Digite seu nick', True, Color.BLACK)
        text_rect = text.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 50))
        # Input
        self.inputs[0].draw(self.screen)

        # Button
        button = pygame.Rect(Size.SCREEN_WIDTH // 2 - 100,
                             Size.SCREEN_HEIGHT // 2 + 100, 200, 50)
        pygame.draw.rect(self.screen, Color.BLACK,
                         button.inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.screen, Color.GREEN, button, border_radius=20)
        button_text = self.font_label.render('Jogar', True, Color.WHITE)
        button_text_rect = button_text.get_rect(center=button.center)

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        # Cursor diferente para o mouse colidindo com o botão ou input
        if button.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.inputs[0].rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Casos para ir para próxima página
        if button.collidepoint(mouse_pos) and mouse_click[0] and self.inputs[0].text != '':
            prox_page = True
        elif self.inputs[0].return_pressed and self.inputs[0].text != '':
            prox_page = True

        self.button_jogar = False
        self.screen.blit(text, text_rect)
        self.screen.blit(image_logo, image_rect)
        self.screen.blit(button_text, button_text_rect)

        if prox_page:
            self.name = self.inputs[0].text
            super().start()
            self.current_page = 'Teste'  # Colocar próxima página que seria a de salas
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            if self.current_input is not None:
                self.current_input.active = False
                self.current_input = None

    def test_page(self):
        '''Página de testes, favor apagar depois'''
        text = self.font_label.render(self.name, True, Color.BLACK)
        text_rect = text.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)

    def handle_chat(self, client, message):
        print(f'~{client["name"]}: {message}')

    def handle_canvas(self, canvas):
        print(f'canvas: {canvas}')


if __name__ == '__main__':
    # Só pra fazer aquele teste maroto
    screen = Screen('localhost', 7001)
    screen.start()
