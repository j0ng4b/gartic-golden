import os

import pygame


class Resource:
    def __init__(self):
        self.fonts = {}
        self.images = {}
        self.sounds = {}

        self.base_path = os.path.dirname(__file__)

    def load_font(self, name, size, path=None):
        if path is not None:
            name = path
        else:
            name = f'{self.base_path}/assets/fonts/{name}.ttf'

        if f'{name}-{size}' not in self.fonts:
            self.fonts[f'{name}-{size}'] = pygame.font.Font(name, size)
        return self.fonts[f'{name}-{size}']

    def load_image(self, name, path=None):
        if path is not None:
            name = path
        else:
            name = f'{self.base_path}/assets/images/{name}.png'

        if name not in self.images:
            self.images[name] = pygame.image.load(name)
        return self.images[name]

    def load_sound(self, name, path=None):
        if path is not None:
            name = path
        else:
            name = f'{self.base_path}/assets/sounds/{name}.ogg'

        if name not in self.sounds:
            self.sounds[name] = pygame.mixer.Sound(name)
        return self.sounds[name]
