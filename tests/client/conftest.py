import os
import sys

import pytest


# Ensure the project root (where 'game' package is located) is in sys.path.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from game.client.base import BaseClient


class DummySocket:
    def __init__(self, *args, **kwargs):
        self.send_calls = []

    def bind(self, address):
        pass

    def recvfrom(self, bufsize):
        return (b'', ('127.0.0.1', 5000))

    def send(self, data):
        self.send_calls.append(data)


class DummyClient(BaseClient):
    def __init__(self, address, port):
        super().__init__(address, port)
        self.socket = DummySocket()

    def handle_chat(self, client, message):
        pass

    def handle_canvas(self, canvas):
        pass

    def get_message(self):
        return self.msgs.pop(0)

    def send_message(self, type, *args, dest='', wait_response=True):
        self.socket.send(f"{dest}/{type}:{';'.join(args)}".encode())

        if wait_response:
            return 'OK'
        return None

@pytest.fixture
def client():
    return DummyClient('127.0.0.1', 8080)
