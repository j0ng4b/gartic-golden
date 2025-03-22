import argparse
import logging

from game.config import Config
from game.client.tui import TUIClient
from game.server import Server


def main(args):
    if args.address is None or args.port is None:
        logging.warning('Nenhum endereço ou porta definido, usando o do ambiente')

        args.address = Config.SERVER_ADDRESS
        args.port = Config.SERVER_PORT


    mode = None
    if args.server:
        mode = Server(args.address, args.port)
    else:
        mode = TUIClient(args.address, args.port)
    mode.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--server', action='store_true', default=False, help='run in server mode')
    parser.add_argument('-a', '--address', type=str, default=None, help='set server address')
    parser.add_argument('-p', '--port', type=int, default=None, help='set server port')

    main(parser.parse_args())

