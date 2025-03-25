def test_error_on_client_unregistred(server):
    addr = ('127.0.0.1', 5001)

    response = server.parse_server_message('ROOM', ['pub', 'notRegistered'], addr)
    assert response == 'Cliente não registrado'


def test_complain_about_extra_arguments(server):
    addr = ('127.0.0.1', 5001)
    server.parse_server_message('REGISTER', ['Bob'], addr)

    response = server.parse_server_message('ROOM', ['pub'], addr)
    assert response == 'Número de argumentos inválido'


def test_complain_about_missing_arguments(server):
    addr = ('127.0.0.1', 5001)
    server.parse_server_message('REGISTER', ['Bob'], addr)

    response = server.parse_server_message('ROOM', ['pub'], addr)
    assert response == 'Número de argumentos inválido'


def test_invalid_room_type(server):
    addr = ('127.0.0.1', 5001)
    server.parse_server_message('REGISTER', ['Bob'], addr)

    response = server.parse_server_message('ROOM', ['invalid', 'RoomName'], addr)
    assert response == 'Tipo da sala inválido'


def test_missing_password_for_private_room(server):
    addr = ('127.0.0.1', 5001)
    server.parse_server_message('REGISTER', ['Bob'], addr)

    response = server.parse_server_message('ROOM', ['priv', 'RoomName'], addr)
    assert response == 'Senha não fornecida para sala privada'


def test_provided_password_for_public_room(server):
    addr = ('127.0.0.1', 5001)
    server.parse_server_message('REGISTER', ['Bob'], addr)

    response = server.parse_server_message('ROOM', ['pub', 'RoomName', 'extra'], addr)
    assert response == 'Sala pública não requer senha'


def test_create_public_room(server):
    addr = ('127.0.0.1', 5002)
    server.parse_server_message('REGISTER', ['Carol'], addr)

    response = server.parse_server_message('ROOM', ['pub', 'CoolRoom'], addr)
    assert response == "1"
    assert len(server.rooms) == 1

    room = server.rooms[0]
    assert room['name'] == 'CoolRoom'
    assert room['password'] is None
    assert room['max_clients'] == 10
    assert addr in room['clients']

    client = server.get_client(addr[0], addr[1])
    assert client is not None
    assert client['room'] == '1'


def test_create_private_room(server):
    addr = ('127.0.0.1', 5003)
    server.parse_server_message('REGISTER', ['Dave'], addr)

    response = server.parse_server_message('ROOM', ['priv', 'SecretRoom', 'mypassword'], addr)
    assert response == "1"

    room = server.rooms[0]
    assert room['name'] == 'SecretRoom'
    assert room['password'] == 'mypassword'
    assert addr in room['clients']

    client = server.get_client(addr[0], addr[1])
    assert client['room'] == '1'

