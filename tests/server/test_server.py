import os
import sys

import pytest


# Ensure the project root (where 'game' package is located) is in sys.path.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from game.server import Server


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


def test_room_client_unregistred(server):
    addr = ('127.0.0.1', 5001)

    # Not registered
    response = server.parse_message('ROOM', ['pub', 'notRegistered'], addr)
    assert response == 'Cliente não registrado'

def test_room_invalid_args(server):
    addr = ('127.0.0.1', 5001)

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
    response = server.parse_message('LIST', ['pub'], addr)
    lines = [line for line in response.strip().split('\n') if line]
    assert len(lines) == 1
    assert 'RoomOne' in lines[0]

    # Filter priv rooms
    response = server.parse_message('LIST', ['priv'], addr)
    lines = [line for line in response.strip().split('\n') if line]
    assert len(lines) == 1
    assert 'RoomTwo' in lines[0]


def test_status_client_unregistred(server):
    addr = ('127.0.0.1', 6001)

    # Test when run the command of unregistred client
    response = server.parse_message('STATUS', [], addr)
    assert response == 'Cliente não registrado'


def test_status_invalid_arguments(server):
    addr = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Big Smoke'], addr)

    # Test if accepting any argument
    response = server.parse_message('STATUS', ['arg'], addr)
    assert response == 'Número de argumentos inválido'

    # Test when client isn't on any room
    response = server.parse_message('STATUS', [], addr)
    assert response == 'Cliente não está em nenhuma sala'


def test_status_format(server):
    addr = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Pikachu'], addr)

    room_code = '1'
    server.rooms = [{
         'name': 'TestRoom',
         'code': room_code,
         'password': None,
         'max_clients': 10,
         'clients': [addr]
    }]

    client = server.get_client(addr[0], addr[1])
    server.clients[client]['room'] = room_code

    response = server.parse_message('STATUS', [], addr)
    assert response == f'pub,TestRoom,{room_code},1,10'


def test_enter_client_unregistred(server):
    addr = ('127.0.0.1', 6001)

    # Test when run the command of unregistred client
    response = server.parse_message('ENTER', ['1'], addr)
    assert response == 'Cliente não registrado'


def test_enter_invalid_arguments(server):
    addr = ('127.0.0.1', 6000)
    server.parse_message('REGISTER', ['Carl Johnson'], addr)

    # Test when more than two arguments are provided.
    response = server.parse_message('ENTER', ['room_code', 'pwd', 'extra'], addr)
    assert response == 'Número de argumentos inválido'


def test_enter_invalid_room_code(server):
    addr = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Shrek'], addr)

    # Simulate the case when get_room returns None (room not found)
    response = server.parse_message('ENTER', ['999'], addr)
    assert response == 'Código da sala inválido'


def test_enter_already_in_room(server):
    addr = ('127.0.0.1', 6002)
    server.parse_message('REGISTER', ['Ash'], addr)

    room_code = '1'
    server.rooms = [{
         'name': 'TestRoom',
         'code': room_code,
         'password': None,
         'max_clients': 10,
         'clients': [addr]
    }]

    # Simulate get_room returning a valid index (0) and a room where the client
    # is already present.
    response = server.parse_message('ENTER', [room_code], addr)
    assert response == 'Cliente já está na sala'


def test_enter_no_password_provided(server):
    addr = ('127.0.0.1', 6003)
    server.parse_message('REGISTER', ['Charlie Brown'], addr)

    room_code = '2'
    server.rooms = [{
         'name': 'PrivateRoom',
         'code': room_code,
         'password': 'secret',
         'max_clients': 10,
         'clients': []
    }]

    # Test entering a private room without providing a password.
    response = server.parse_message('ENTER', [room_code], addr)
    assert response == 'Senha não fornecida'


def test_enter_incorrect_password(server):
    addr = ('127.0.0.1', 6004)
    server.parse_message('REGISTER', ['Snoopy'], addr)

    room_code = '3'
    server.rooms = [{
         'name': 'PrivateRoom',
         'code': room_code,
         'password': 'secret',
         'max_clients': 10,
         'clients': []
    }]

    # Test entering a private room with an incorrect password.
    response = server.parse_message('ENTER', [room_code, 'wrongpass'], addr)
    assert response == 'Senha da sala está incorreta'


def test_get_client(server):
    addr = ('127.0.0.1', 5008)
    assert server.get_client(addr[0], addr[1]) is None

    server.parse_message('REGISTER', ['Grace'], addr)
    index = server.get_client(addr[0], addr[1])
    assert index is not None
    assert server.clients[index]['name'] == 'Grace'

