import os
import random

import pygame


class Size():
    # Tamanho da tela
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600


class Color():
    # Cores
    GOLDEN = (243, 202, 76)
    DARK_GOLDEN = (184, 134, 11)
    LIGHT_YELLOW = (254, 214, 91)
    GREEN = (128, 225, 99)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    LIGHT_GRAY = (169, 169, 169)
    HONEY = (251, 189, 0)
    RED = (218, 41, 44)
    LIGHT_GOLD = (254, 214, 91)


class InputField():
    def __init__(self, rect: pygame.rect, font: pygame.font.Font, placeholder=''):
        self.rect = rect
        self.font = font
        self.text = ''
        self.active = False
        self.placeholder = placeholder
        self.return_pressed = False
        self.text_offset = 0
        self.padding = 5
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

        if self.active and event.type == pygame.KEYDOWN:
            self.time = pygame.time.get_ticks()
            self.cursor_visible = True
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0 and len(self.text) > 0:
                    self.text = self.text[:self.cursor_pos -
                                          1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE and self.cursor_pos < len(self.text):
                self.text = self.text[:self.cursor_pos] + \
                    self.text[self.cursor_pos+1:]
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif event.key == pygame.K_RETURN:
                if self.text:
                    self.return_pressed = True
            else:
                self.text = self.text[:self.cursor_pos] + \
                    event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1
            self.update_text_offset()

    def update_text_offset(self):
        max_width = self.rect.width - 2 * self.padding
        cursor_pixel_pos = self.font.size(self.text[:self.cursor_pos])[0]
        text_width = self.font.size(self.text)[0]
        self.text_offset = max(
            0, min(cursor_pixel_pos, text_width - max_width, cursor_pixel_pos - max_width))

    def draw(self, screen):
        pygame.draw.rect(screen, Color.WHITE, self.rect, border_radius=8)
        pygame.draw.rect(screen, Color.BLACK, self.rect, 2, border_radius=8)

        display_text = self.text if self.text else self.placeholder
        text_color = Color.BLACK if self.text else Color.LIGHT_GRAY
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


def load_words(theme: str, max_rounds: int):
    '''
        Retorna palavras aleatórias de acordo com um tema e número de rodadas
        (atualmente no máximo até 20).
    '''
    path_file = os.path.join(os.path.dirname(os.path.dirname(
        os.path.dirname(__file__))), 'data', 'words.txt')
    with open(path_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for line in lines:
        if line.startswith(theme + ","):
            words = line.strip().split(",")[1:]
            return random.sample(words, max_rounds)
    return []