import pygame

from game.screen.constants import Color, Size


class BaseComponent:
    def __init__(self):
        # Tela de desenho
        self.surface = None

        # Gerenciador de assets
        self.resource = None

    def init(self, surface, resource):
        '''
        Inicializa o componente
        --------------------

        Chamada para inicializar os elementos que estão no componente. Essa função
        deve ser chamada antes de usar o componente e deve ser chamada apenas uma vez.
        '''

        self.surface = surface
        self.resource = resource

    def update(self):
        '''
        Atualiza o componente
        --------------------

        Chamada para atualizar os elementos que estão no componente.
        '''
        pass

    def draw(self):
        '''
        Desenha o componente
        --------------------

        Chamada para desenhar os elementos que estão no componente.
        '''
        pass

    def handle_input(self, event):
        '''
        Trata o input do componente
        --------------------

        Chamada para tratar o input do componente.
        '''
        pass


class Label(BaseComponent):
    def __init__(self, text, x, y, text_color=Color.WHITE, font_size=40):
        self.text = text
        self.text_color = text_color

        self.x = x
        self.y = y

        self.font = None
        self.font_size = font_size

        self.label_rect = None
        self.label_surface = None

    def init(self, surface, resource):
        super().init(surface, resource)

        self.font = resource.load_font('Acme-Regular', self.font_size)
        self.update_text()

    def draw(self):
        if self.surface is None or self.font is None:
            return
        self.surface.blit(self.label_surface, self.label_rect)

    def update_text(self):
        if self.font is None:
            return

        self.label_surface = self.font.render(self.text, True, self.text_color)
        self.label_rect = self.label_surface.get_rect(center=(self.x, self.y))

    def set_text(self, text):
        if self.text == text:
            return

        self.text = text
        self.update_text()

    def set_color(self, color):
        if self.text_color == color:
            return

        self.text_color = color
        self.update_text()


class Image(BaseComponent):
    def __init__(self, path, x, y, width=None, height=None):
        self.path = path
        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.image_surface = None
        self.image_rect = None

    def init(self, surface, resource):
        super().init(surface, resource)

        self.image_surface = resource.load_image(self.path)
        if self.width is not None and self.height is not None:
            self.image_surface = pygame.transform.scale(
                self.image_surface, (self.width, self.height))
        self.image_rect = self.image_surface.get_rect(center=(self.x, self.y))

    def draw(self):
        if self.surface is None or self.image_surface is None:
            return
        self.surface.blit(self.image_surface, self.image_rect)


class Button(BaseComponent):
    def __init__(self, text, x, y, width, height, on_click=None, on_hover=None):
        self.text = text

        self.on_click = on_click
        self.on_hover = on_hover

        self.rect = pygame.Rect(x, y, width, height)

        self.button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.button_surface.fill(Color.GREEN)

        self.round_clip = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(self.round_clip, Color.WHITE, (0, 0, width, height), border_radius=20)

        self.font = None

    def init(self, surface, resource):
        super().init(surface, resource)

        self.font = resource.load_font('Acme-Regular', 30)
        self.update_text()

    def draw(self):
        if self.surface is None:
            return

        self.surface.blit(self.button_surface, self.rect)

    def handle_input(self, event):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                if self.on_click is not None:
                    self.on_click()
        elif event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if self.on_hover is not None:
                    self.on_hover()
            else:
                if self.on_hover is not None:
                    self.on_hover(False)

    def set_text(self, text):
        if self.text == text:
            return

        self.text = text
        self.update_text()

    def update_text(self):
        if self.font is None:
            return

        text_surface = self.font.render(self.text, True, Color.WHITE)
        text_rect = text_surface.get_rect()

        self.button_surface.fill(Color.GREEN)
        self.button_surface.blit(text_surface, [
            self.rect.width / 2 - text_rect.width / 2,
            self.rect.height / 2 - text_rect.height / 2
        ])

        self.button_surface.blit(self.round_clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


class InputField(BaseComponent):
    def __init__(self, rect, placeholder='', on_enter=None):
        self.rect = rect

        self.text = []
        self.font = None
        self.placeholder = placeholder

        self.active = False
        self.padding = 5
        self.text_offset = 0

        # Processamento de teclas
        self.key_pressed = None
        self.key_repeat = False
        self.key_repeat_time = 0
        self.key_repeat_delay = 20

        self.input_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        self.input_surface.fill(Color.BLACK)

        # Arredonda as bordas do campo de entrada
        self.round_clip = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(self.round_clip, Color.WHITE, (0, 0, rect.width, rect.height), border_radius=8)
        self.input_surface.blit(self.round_clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        # Define a área de recorte do campo de entrada
        self.input_surface.set_clip(pygame.Rect(
            self.padding,
            self.padding,
            self.rect.width - (self.padding * 2),
            self.rect.height - (self.padding * 2)
        ))

        # Cursor
        self.cursor_pos = 0
        self.cursor_time = 0
        self.cursor_width = 2
        self.cursor_visible = True
        self.cursor_interval = 500

        self.on_enter = on_enter

    def init(self, surface, resource):
        super().init(surface, resource)

        self.font = resource.load_font('Acme-Regular', 30)

    def update(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)

        if not self.active:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_time > self.cursor_interval:
            self.cursor_visible = not self.cursor_visible
            self.cursor_time = current_time

        if self.key_pressed is not None:
            # Repetição de tecla
            if self.key_repeat and current_time - self.key_repeat_time < self.key_repeat_delay:
                return

            # A repetição de tecla só passa a valer depois de 200ms da primeira tecla
            if not self.key_repeat:
                self.key_repeat = True
                self.key_repeat_time = current_time + 200
            else:
                self.key_repeat_time = current_time


            # Se a tecla pressionada for uma tecla de controle, trata o evento
            if self.key_pressed[0] == pygame.K_BACKSPACE:
                if len(self.text) > 0 and self.cursor_pos > 0:
                    self.cursor_pos -= 1
                    self.text.pop(self.cursor_pos)
            elif self.key_pressed[0] == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text.pop(self.cursor_pos)
            elif self.key_pressed[0] == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif self.key_pressed[0] == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif self.key_pressed[0] == pygame.K_HOME:
                self.cursor_pos = 0
            elif self.key_pressed[0] == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif self.key_pressed[0] == pygame.K_RETURN:
                if self.on_enter is not None:
                    self.on_enter(''.join(self.text))
            else:
                self.text.insert(self.cursor_pos, self.key_pressed[1])
                self.cursor_pos += 1

            self.update_text_offset()

    def draw(self):
        if self.surface is None or self.font is None:
            return

        self.input_surface.fill(Color.WHITE)

        text = ''.join(self.text) if self.text else self.placeholder
        text_color = Color.BLACK if self.text else Color.LIGHT_GRAY
        text_surface = self.font.render(text, True, text_color)

        text_rect = text_surface.get_rect(
            midleft=(self.padding - self.text_offset, self.rect.height // 2)
        )
        self.input_surface.blit(text_surface, text_rect)

        # Desenha o cursor
        if self.active and self.cursor_visible:
            cursor_pixel_pos = self.font.size(text[:self.cursor_pos])[0]

            cursor_x = self.padding + cursor_pixel_pos - self.text_offset
            cursor_x = max(self.padding, min(cursor_x, self.rect.width - self.padding))

            pygame.draw.line(
                self.input_surface, (0, 0, 0),
                (cursor_x, self.padding),
                (cursor_x, self.rect.height - self.padding),
                self.cursor_width
            )

        self.surface.blit(self.input_surface, self.rect)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)

            # Se o campo de entrada estiver ativo, o cursor deve ser posicionado no final
            # do texto e o tempo do cursor deve ser atualizado
            if self.active:
                self.cursor_pos = len(self.text)
                self.cursor_time = pygame.time.get_ticks()
                self.cursor_visible = True

                self.update_text_offset()

        if event.type == pygame.KEYDOWN:
            if not self.active:
                return

            self.cursor_time = pygame.time.get_ticks()
            self.cursor_visible = True

            self.key_pressed = (event.key, event.unicode)
            self.key_repeat = False
            self.key_repeat_time = pygame.time.get_ticks()
        elif event.type == pygame.KEYUP:
            if not self.active:
                return

            self.key_pressed = None

    def update_text_offset(self):
        if self.font is None:
            return

        max_width = self.rect.width - (self.padding * 2)
        cursor_pixel_pos = self.font.size(''.join(self.text[:self.cursor_pos]))[0]
        text_width = self.font.size(''.join(self.text))[0]
        self.text_offset = max(
            0, min(text_width - max_width, cursor_pixel_pos - max_width))

    def get_text(self):
        return ''.join(self.text)

    def set_text(self, text):
        if self.text == text:
            return

        self.text = list(text)
        self.cursor_pos = len(self.text)
        self.update_text_offset()


class Window(BaseComponent):
    def __init__(self, width, height):
        self.visible = True

        self.rect = pygame.Rect(
            Size.SCREEN_WIDTH // 2 - width // 2,
            Size.SCREEN_HEIGHT // 2 - height // 2,
            width, height
        )
        self.window_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Arredonda as bordas da janela
        self.round_clip = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(self.round_clip, Color.WHITE, (0, 0, width, height), border_radius=20)

        self.components = []

    def init(self, surface, resource):
        super().init(surface, resource)

    def draw(self):
        if self.surface is None or not self.visible:
            return

        self.window_surface.fill(Color.LIGHT_GRAY)
        self.window_surface.blit(self.round_clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        for component in self.components:
            component.draw()
        self.surface.blit(self.window_surface, self.rect)

    def update(self):
        if not self.visible:
            return

        for component in self.components:
            component.update()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            return

        for component in self.components:
            component.handle_input(event)

    def add_component(self, component):
        component.init(self.window_surface, self.resource)
        self.components.append(component)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

