import os
import random


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