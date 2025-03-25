def test_complain_about_client_unregistred(server):
    addr = ('127.0.0.1', 6001)

    response = server.parse_server_message('ENTER', ['1'], addr)
    assert response == 'Cliente não registrado'


def test_complain_about_exta_arguments(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Carl Johnson'], addr)

    response = server.parse_server_message('ENTER', ['room_code', 'pwd', 'extra'], addr)
    assert response == 'Número de argumentos inválido'


def test_invalid_room_code(server):
    addr = ('127.0.0.1', 6001)
    server.parse_server_message('REGISTER', ['Shrek'], addr)

    response = server.parse_server_message('ENTER', ['999'], addr)
    assert response == 'Código da sala inválido'


def test_client_already_on_the_room(server):
    addr = ('127.0.0.1', 6002)
    server.parse_server_message('REGISTER', ['Ash'], addr)

    room_code = '1'
    server.rooms = [{
        'name': 'TestRoom',
        'code': room_code,
        'password': None,
        'max_clients': 10,
        'clients': []
    }]
    server.parse_server_message('ENTER', [room_code], addr)

    response = server.parse_server_message('ENTER', [room_code], addr)
    assert response == 'Cliente já está na sala'


def test_client_already_on_other_room(server):
    addr = ('127.0.0.1', 6002)
    server.parse_server_message('REGISTER', ['Ash'], addr)

    room_code = '1'
    server.rooms = [{
        'name': 'Room 1',
        'code': room_code,
        'password': None,
        'max_clients': 10,
        'clients': []
    },{
        'name': 'Room 2',
        'code': '2',
        'password': None,
        'max_clients': 10,
        'clients': []
    }]
    server.parse_server_message('ENTER', ['2'], addr)

    response = server.parse_server_message('ENTER', [room_code], addr)
    assert response == 'Cliente já está em outra sala'


def test_when_no_password_is_provided(server):
    addr = ('127.0.0.1', 6003)
    server.parse_server_message('REGISTER', ['Charlie Brown'], addr)

    room_code = '2'
    server.rooms = [{
        'name': 'PrivateRoom',
        'code': room_code,
        'password': 'secret',
        'max_clients': 10,
        'clients': []
    }]

    response = server.parse_server_message('ENTER', [room_code], addr)
    assert response == 'Senha não fornecida'


def test_when_password_is_incorrect(server):
    addr = ('127.0.0.1', 6004)
    server.parse_server_message('REGISTER', ['Snoopy'], addr)

    room_code = '3'
    server.rooms = [{
        'name': 'PrivateRoom',
        'code': room_code,
        'password': 'secret',
        'max_clients': 10,
        'clients': []
    }]

    response = server.parse_server_message('ENTER', [room_code, 'wrongpass'], addr)
    assert response == 'Senha da sala está incorreta'


def test_enter_private_room(server):
    addr = ('127.0.0.1', 6004)
    server.parse_server_message('REGISTER', ['Snoopy'], addr)

    room_code = '3'
    server.rooms = [{
        'name': 'PrivateRoom',
        'code': room_code,
        'password': 'secret',
        'max_clients': 10,
        'clients': []
    }]

    response = server.parse_server_message('ENTER', [room_code, 'secret'], addr)
    assert response == 'OK'

    client = server.clients[0]
    assert client['room'] == room_code


def test_enter_public_room(server):
    addr = ('127.0.0.1', 6004)
    server.parse_server_message('REGISTER', ['Snoopy'], addr)

    room_code = '1'
    server.rooms = [{
        'name': 'TestRoom',
        'code': room_code,
        'password': None,
        'max_clients': 10,
        'clients': []
    }]

    response = server.parse_server_message('ENTER', [room_code], addr)
    assert response == 'OK'

    client = server.clients[0]
    assert client['room'] == room_code


def test_send_connect_message_to_clients(server):
    addr1 = ('127.0.0.1', 6004)
    server.parse_server_message('REGISTER', ['Snoopy'], addr1)
    room_code = server.parse_server_message('ROOM', ['pub', 'Room'], addr1)

    addr2 = ('127.0.0.1', 6003)
    server.parse_server_message('REGISTER', ['Charlie Brown'], addr2)

    response = server.parse_server_message('ENTER', [room_code], addr2)
    assert response == 'OK'
    assert len(server.rooms[0]['clients']) == 2

    message_0, addr_0 = server.socket.sendto_calls[0]
    message_1, addr_1 = server.socket.sendto_calls[1]
    assert message_0.startswith(b'/CONNECT:')
    assert addr_0 == addr1

    assert message_1.startswith(b'/CONNECT:')
    assert addr_1 == addr2
