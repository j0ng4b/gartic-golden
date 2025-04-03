
class BasePage:
    def __init__(self, name):
        self.name = name

        # Utiliza o goto_page para ir para outra página
        # quando necessário
        self.goto_page = None

    def init(self, goto_page):
        '''
        Inicializa a página
        --------------------

        Chamada para inicializar os elementos que estão na página. Essa função
        deve ser chamada antes de usar a página e deve ser chamada apenas uma vez.
        '''

        self.goto_page = goto_page

    def update(self):
        '''
        Atualiza a página
        --------------------
        
        Chamada para atualizar os elementos que estão na página.
        '''
        pass

    def draw(self):
        '''
        Desenha a página
        --------------------

        Chamada para desenhar os elementos que estão na página.
        '''
        pass

    def handle_input(self):
        '''
        Lida com a entrada do usuário
        --------------------

        Chamada para lidar com a entrada do usuário na página.
        '''
        pass

    def reset(self):
        '''
        Reseta a página
        --------------------

        Chamada para resetar os elementos que estão na página.
        '''
        pass
