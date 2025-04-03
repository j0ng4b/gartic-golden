import abc


class BasePage(abc.ABC):
    def __init__(self, name):
        self.name = name

        # Utiliza o goto_page para ir para outra página
        # quando necessário
        self.goto_page = None

    @abc.abstractmethod
    def init(self, goto_page):
        '''
        Inicializa a página
        --------------------

        Chamada para inicializar os elementos que estão na página. Essa função
        deve ser chamada antes de usar a página e deve ser chamada apenas uma vez.
        '''

        self.goto_page = goto_page

    @abc.abstractmethod
    def update(self):
        '''
        Atualiza a página
        --------------------
        
        Chamada para atualizar os elementos que estão na página.
        '''
        pass

    @abc.abstractmethod
    def draw(self):
        '''
        Desenha a página
        --------------------

        Chamada para desenhar os elementos que estão na página.
        '''
        pass

    @abc.abstractmethod
    def handle_input(self, event):
        '''
        Lida com a entrada do usuário
        --------------------

        Chamada para lidar com a entrada do usuário na página.
        '''
        pass

    @abc.abstractmethod
    def reset(self):
        '''
        Reseta a página
        --------------------

        Chamada para resetar os elementos que estão na página.
        '''
        pass


class RegisterPage(BasePage):
    def __init__(self):
        super().__init__('register')

    def init(self, goto_page):
        super().init(goto_page)
        pass

    def update(self):
        pass

    def draw(self):
        pass

    def handle_input(self, event):
        pass

    def reset(self):
        pass
