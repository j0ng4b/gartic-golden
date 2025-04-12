import argparse
import logging

from game.config import Config


def main(args):
    if args.address is None or args.port is None:
        logging.warning('Nenhum endereço ou porta definido, usando o do ambiente')

        args.address = Config.SERVER_ADDRESS
        args.port = Config.SERVER_PORT


    mode = None
    if args.server:
        from game.server import Server
        mode = Server(args.address, args.port)
    elif args.gui:
        from game.screen.screen import Screen
        mode = Screen(args.address, args.port)

        # Registra as páginas
        import game.screen.pages as pages
        mode.register_page('register', pages.RegisterPage())
        mode.register_page('rooms', pages.RoomsPage())
        mode.register_page('play', pages.PlayPage())

        # A primeira página a ser carregada é a de registro do usuário
        mode.goto_page('register')
    else:
        from game.client.tui import TUIClient
        mode = TUIClient(args.address, args.port)
    mode.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--server', action='store_true', default=False, help='run in server mode')
    parser.add_argument('-a', '--address', type=str, default=None, help='set server address')
    parser.add_argument('-g', '--gui', action='store_true', default=False, help='run with graphical interface')
    parser.add_argument('-p', '--port', type=int, default=None, help='set server port')

    main(parser.parse_args())

