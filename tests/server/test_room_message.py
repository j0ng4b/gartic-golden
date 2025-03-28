def test_error_on_client_unregistred(server):
    addr = ('127.0.0.1', 6000)

    response = server.parse_server_message('ROOM', ['pub', 'notRegistered', 'Test'], addr)
    assert response == 'Cliente não registrado'


def test_complain_about_extra_arguments(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ROOM', ['pub', 'foo', 'bar', 'baq', 'extra'], addr)
    assert response == 'Número de argumentos inválido'


def test_complain_about_missing_arguments(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ROOM', ['pub'], addr)
    assert response == 'Número de argumentos inválido'


def test_invalid_room_type(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ROOM', ['invalid', 'RoomName', 'Test'], addr)
    assert response == 'Tipo da sala inválido'


def test_invalid_room_name(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ROOM', ['pub', '', 'Test'], addr)
    assert response == 'Nome da sala inválido'


def test_missing_password_for_private_room(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ROOM', ['priv', 'RoomName', 'Test'], addr)
    assert response == 'Senha não fornecida para sala privada'


def test_provided_password_for_public_room(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ROOM', ['pub', 'RoomName', 'Test', 'extra'], addr)
    assert response == 'Sala pública não requer senha'


def test_create_room_with_client_on_another_room(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)
    server.parse_server_message('ROOM', ['pub', 'TestRoom', 'Test'], addr)

    response = server.parse_server_message('ROOM', ['pub', 'AnotherRoom', 'Test'], addr)
    assert response == 'Cliente já está em uma sala'


def test_create_public_room(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ROOM', ['pub', 'CoolRoom', 'Test'], addr)
    assert response == "1"
    assert len(server.rooms) == 1

    room = server.rooms[0]
    assert room['name'] == 'CoolRoom'
    assert room['password'] is None
    assert room['max_clients'] == 10
    assert any(client[1] == addr[0] and client[2] == addr[1] for client in room['clients'])

    client = server.get_client(addr[0], addr[1])
    assert client is not None
    assert client['room'] == '1'


def test_create_private_room(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ROOM', ['priv', 'SecretRoom', 'Test', 'mypassword'], addr)
    assert response == "1"

    room = server.rooms[0]
    assert room['name'] == 'SecretRoom'
    assert room['password'] == 'mypassword'
    assert any(client[1] == addr[0] and client[2] == addr[1] for client in room['clients'])

    client = server.get_client(addr[0], addr[1])
    assert client['room'] == '1'

