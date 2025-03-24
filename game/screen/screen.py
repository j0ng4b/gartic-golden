import pygame
import os
from game.client.tui import TUIClient
from .utils.utilities import *

class InputField():
    def __init__(self, rect, font, placeholder=''):
        self.rect = rect
        self.font = font
        self.text = ''
        self.active = False
        self.placeholder = placeholder
        self.time = pygame.time.get_ticks()
        self.cursor_interval = 400
        self.cursor_visible = True
        self.return_pressed = False
        self.border_radius = 8

    def handle_event(self, event):
        if self.active:
            self.return_pressed = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.return_pressed = True
                else:
                    self.text += event.unicode

    def draw(self, screen):
        current_time = pygame.time.get_ticks()
        if current_time - self.time >= self.cursor_interval:
            self.cursor_visible = not self.cursor_visible
            self.time = current_time

        pygame.draw.rect(screen, Color.WHITE, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, Color.BLACK, self.rect, 2, border_radius=self.border_radius)

        display_text = None
        text_color = None
        if self.text:
            display_text = self.text
            text_color = Color.BLACK
        else:
            display_text = self.placeholder
            text_color = Color.LIGHT_GRAY

        text = self.font.render(display_text, True, text_color)
        input_rect = text.get_rect(topleft=(self.rect.x + 10, self.rect.y + 5))
        screen.blit(text, input_rect)

        if self.active and self.cursor_visible:
            cursor_pos = input_rect.right, input_rect.top
            cursor_height = input_rect.height
            pygame.draw.line(screen, text_color, cursor_pos,
                             (cursor_pos[0], cursor_pos[1] + cursor_height - 4), 2)


class Screen():
    def __init__(self, client: TUIClient):
        pygame.init()
        pygame.display.set_icon(pygame.image.load(os.path.join(
            os.path.dirname(__file__), 'assets', 'ico.png')))
        pygame.display.set_caption('Gartic Golden')

        self.client = client

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
        if self.current_page == 'Teste':
            self.test_page()

    def register_page(self):
        prox_page = False
        # Logo
        image_logo = pygame.image.load(os.path.join(
            os.path.dirname(__file__), 'assets', 'logo.png'))
        image_rect = image_logo.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 200))
        # Label
        text = self.font_label.render('Digite seu nick:', True, Color.BLACK)
        text_rect = text.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 50))
        # Input
        self.inputs[0].draw(self.screen)

        # Button
        button = pygame.Rect(Size.SCREEN_WIDTH // 2 - 100, Size.SCREEN_HEIGHT // 2 + 100, 200, 50)
        pygame.draw.rect(self.screen, Color.BLACK, button.inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.screen, Color.GREEN, button, border_radius=20)
        button_text = self.font_label.render('Jogar', True, Color.WHITE)
        button_text_rect = button_text.get_rect(center=button.center)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

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
            client.name = self.inputs[0].text # Atribui o nick do cliente
            self.current_page = 'Teste'  # Colocar próxima página que seria a de salas
            if self.current_input is not None: 
                self.current_input.active = False
                self.current_input = None

    def test_page(self):
        '''Página de testes, favor apagar depois'''
        text = self.font_label.render(self.client.name, True, Color.BLACK)
        text_rect = text.get_rect(
            center=(Size.SCREEN_WIDTH // 2, Size.SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)


if __name__ == '__main__':
    # Só para testar
    client = TUIClient('localhost', 7001)
    screen = Screen(client)
    screen.start()
