from game.screen.utils.utilities import *


def register_page(self):
    '''Exibe a tela de registro onde o jogador pode inserir um apelido.'''
    self.inputs[0].draw(self.screen)
    pygame.draw.rect(self.screen, Color.BLACK,
                     self.button_play_border, border_radius=20)
    pygame.draw.rect(self.screen, Color.GREEN,
                     self.button_play_rect, border_radius=20)
    self.screen.blit(self.text_label_nick, self.text_label_nick_rect)
    self.screen.blit(self.image_logo_big, self.image_logo_big_rect)
    self.screen.blit(self.button_play_text, self.button_play_text_rect)
