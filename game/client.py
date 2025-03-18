import socket
import threading

from game.config import Config


class Client:
    def __init__(self):
        if Config.SERVER_ADDRESS is None or Config.SERVER_PORT is None:
            raise ValueError('SERVER_ADDRESS and SERVER_PORT must be set in the environment')

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((Config.SERVER_ADDRESS, int(Config.SERVER_PORT)))

        # Inicializa a thread que vai lidar com a comunicação
        thread = threading.Thread(target=self.handle_communication)
        thread.daemon = True
        thread.start()

    def start(self):
        ...

    def handle_input(self):
        ...

    def handle_communication(self):
        ...

