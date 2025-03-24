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
        self.sendto_calls = []

    def bind(self, address):
        pass

    def recvfrom(self, bufsize):
        return (b'', ('127.0.0.1', 5000))

    def sendto(self, data, address):
        self.sendto_calls.append((data, address))


class DummyClient(BaseClient):
    def __init__(self, address, port):
        super().__init__(address, port)
        self.socket = DummySocket()

    def handle_chat(self, client, message):
        client.setdefault('handled_chats', []).append(message)

    def get_message(self, address):
        if self.msgs.get(address):
            return self.msgs[address].pop(0)
        return ''

    def send_message(self, type, *args, address=None, wait_response=True):
        if address is None:
            address = self.address

        msg = f"{type}:{';'.join(args)}"
        self.socket.sendto(msg.encode(), address)

        if wait_response:
            return "OK"
        return None

@pytest.fixture
def client():
    return DummyClient('localhost', 8080)

