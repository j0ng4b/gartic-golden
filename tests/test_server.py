import os
import sys
import socket

import pytest

# Ensure the project root (where 'game' package is located) is in sys.path.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
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


def test_init_requires_address_and_port():
    with pytest.raises(ValueError):
        Server(None, 5000)

    with pytest.raises(ValueError):
        Server('127.0.0.1', None)


def test_register_invalid_args(server):
    addr = ('127.0.0.1', 5000)

    # Zero arguments
    response = server.parse_message('REGISTER', [], addr)
    assert response == 'Número de argumentos inválido'

    # Empty name
    response = server.parse_message('REGISTER', [''], addr)
    assert response == 'Nome de jogador inválido'


def test_register_success(server):
    addr = ('127.0.0.1', 5000)

    response = server.parse_message('REGISTER', ['Alice'], addr)
    assert response == 'OK'
    assert any(client['name'] == 'Alice' for client in server.clients)


def test_room_invalid_args(server):
    addr = ('127.0.0.1', 5001)

    # Not registered
    response = server.parse_message('ROOM', ['pub', 'notRegistered'], addr)
    assert response == 'Cliente não registrado'

    # Register a client to create a room
    server.parse_message('REGISTER', ['Bob'], addr)

    # Not enough arguments
    response = server.parse_message('ROOM', ['pub'], addr)
    assert response == 'Número de argumentos inválido'

    # Invalid room type
    response = server.parse_message('ROOM', ['invalid', 'RoomName'], addr)
    assert response == 'Tipo da sala inválido'

    # For private room missing password
    response = server.parse_message('ROOM', ['priv', 'RoomName'], addr)
    assert response == 'Senha não fornecida para sala privada'

    # For public room with extra argument
    response = server.parse_message('ROOM', ['pub', 'RoomName', 'extra'], addr)
    assert response == 'Sala pública não requer senha'


def test_room_public_success(server):
    addr = ('127.0.0.1', 5002)
    server.parse_message('REGISTER', ['Carol'], addr)

    # Room code should be 1
    response = server.parse_message('ROOM', ['pub', 'CoolRoom'], addr)
    assert response == "1"
    assert len(server.rooms) == 1

    # Check room details
    room = server.rooms[0]
    assert room['name'] == 'CoolRoom'
    assert room['password'] is None
    assert room['max_clients'] == 10
    assert addr in room['clients']

    # Check client room assignment
    client_index = server.get_client(addr[0], addr[1])
    assert client_index is not None
    assert server.clients[client_index]['room'] == "1"


def test_room_private_success(server):
    addr = ('127.0.0.1', 5003)
    server.parse_message('REGISTER', ['Dave'], addr)

    # Create a private room
    response = server.parse_message('ROOM', ['priv', 'SecretRoom', 'mypassword'], addr)
    assert response == "1"

    # Check room details
    room = server.rooms[0]
    assert room['name'] == 'SecretRoom'
    assert room['password'] == 'mypassword'
    assert addr in room['clients']

    # Check client room assignment
    client_index = server.get_client(addr[0], addr[1])
    assert server.clients[client_index]['room'] == "1"


def test_list_rooms(server):
    addr = ('127.0.0.1', 5007)

    # Initially empty
    response = server.parse_message('LIST', [], addr)
    assert response == ''

    # Create two rooms
    addr1 = ('127.0.0.1', 5005)
    server.parse_message('REGISTER', ['Eve'], addr1)
    server.parse_message('ROOM', ['pub', 'RoomOne'], addr1)

    addr2 = ('127.0.0.1', 5006)
    server.parse_message('REGISTER', ['Frank'], addr2)
    server.parse_message('ROOM', ['priv', 'RoomTwo', 'secret'], addr2)

    # List without filter should return two lines
    response = server.parse_message('LIST', [], addr)
    lines = response.strip().split('\n')
    assert len(lines) == 2

    # Filter pub rooms
    response_pub = server.parse_message('LIST', ['pub'], addr)
    lines_pub = [line for line in response_pub.strip().split('\n') if line]
    assert len(lines_pub) == 1
    assert 'RoomOne' in lines_pub[0]

    # Filter priv rooms
    response_priv = server.parse_message('LIST', ['priv'], addr)
    lines_priv = [line for line in response_priv.strip().split('\n') if line]
    assert len(lines_priv) == 1
    assert 'RoomTwo' in lines_priv[0]


def test_get_client(server):
    addr = ('127.0.0.1', 5008)
    assert server.get_client(addr[0], addr[1]) is None

    server.parse_message('REGISTER', ['Grace'], addr)
    index = server.get_client(addr[0], addr[1])
    assert index is not None
    assert server.clients[index]['name'] == 'Grace'

