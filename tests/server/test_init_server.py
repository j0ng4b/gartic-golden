import pytest

from game.server import Server


def test_server_require_address():
    with pytest.raises(ValueError):
        Server(None, 5000)

def test_server_require_port():
    with pytest.raises(ValueError):
        Server('127.0.0.1', None)

