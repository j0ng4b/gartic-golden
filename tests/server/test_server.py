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

