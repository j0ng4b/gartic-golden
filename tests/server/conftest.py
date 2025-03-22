import os
import sys
import socket

import pytest


# Ensure the project root (where 'game' package is located) is in sys.path.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from game.server import Server


@pytest.fixture(autouse=True)
def patch_socket(monkeypatch):
    class DummySocket:
        def __init__(self, *args, **kwargs):
            pass

        def bind(self, address):
            pass

        def recvfrom(self, bufsize):
            return (b'', ('127.0.0.1', 5000))

        def sendto(self, data, address):
            pass

    monkeypatch.setattr(socket, 'socket', lambda *args, **kwargs: DummySocket(*args, **kwargs))


@pytest.fixture
def server():
    return Server('127.0.0.1', 5000)


