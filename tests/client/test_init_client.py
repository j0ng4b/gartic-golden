import socket

import pytest

from conftest import DummyClient


def test_init_valid(client):
    assert client.address == (socket.gethostbyname('localhost'), 8080)


def test_init_invalid_address():
    with pytest.raises(ValueError):
        DummyClient(None, 8080)


def test_init_invalid_port():
    with pytest.raises(ValueError):
        DummyClient('localhost', None)

