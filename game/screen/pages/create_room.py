from game.screen.utils.utilities import *

def create_room_page(self):
        self.screen.blit(self.image_logo_big, self.image_logo_big_rect)
        for _, label in enumerate(self.create_labels):
            text = self.font_label.render(label['text'], True, Color.BLACK)
            self.screen.blit(text, text.get_rect(center=label['pos']))
        self.inputs[3].draw(self.screen)
        self.inputs[4].draw(self.screen)
        self.inputs[5].draw(self.screen)
        pygame.draw.rect(self.screen, Color.WHITE,
                         self.theme_rect, border_radius=5)
        pygame.draw.rect(self.screen, Color.BLACK,
                         self.theme_rect, 2, border_radius=5)
        theme_text = self.font_input_chat.render(self.theme, True, Color.BLACK)
        self.screen.blit(theme_text, (self.theme_rect.x +
                         10, self.theme_rect.y + 10))
        pygame.draw.rect(self.screen, Color.GOLDEN,
                         self.change_theme_button, border_radius=5)
        self.screen.blit(self.refresh_icon, self.change_theme_button)
        pygame.draw.rect(self.screen, Color.BLACK,
                         self.button_back_rect.inflate(2, 2), border_radius=20)
        pygame.draw.rect(self.screen, Color.RED,
                         self.button_back_rect, border_radius=20)
        pygame.draw.rect(self.screen, Color.BLACK, self.button_create_prox_rect.inflate(
            2, 2), border_radius=20)
        pygame.draw.rect(self.screen, Color.GREEN,
                         self.button_create_prox_rect, border_radius=20)
        self.screen.blit(self.button_create_prox_text, self.button_create_prox_text.get_rect(
            center=self.button_create_prox_rect.center))
        self.screen.blit(self.button_back_text, self.button_back_text.get_rect(
            center=self.button_back_rect.center))