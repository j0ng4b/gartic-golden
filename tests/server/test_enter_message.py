import pytest


@pytest.fixture
def public_room(server):
    addr = ('127.0.0.1', 2000)
    server.parse_server_message('REGISTER', ['TestUser'], addr)
    server.parse_server_message('ROOM', ['pub', 'TestRoom', 'Test'], addr)


@pytest.fixture
def private_room(server):
    addr = ('127.0.0.1', 2000)
    server.parse_server_message('REGISTER', ['TestUser'], addr)
    server.parse_server_message('ROOM', ['priv', 'TestRoom', 'Test', 'password'], addr)



def test_complain_about_client_unregistred(server):
    addr = ('127.0.0.1', 6000)

    response = server.parse_server_message('ENTER', ['1'], addr)
    assert response == 'Cliente não registrado'


def test_complain_about_exta_arguments(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ENTER', ['room_code', 'pwd', 'extra'], addr)
    assert response == 'Número de argumentos inválido'


def test_invalid_room_code(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ENTER', ['999'], addr)
    assert response == 'Código da sala inválido'


@pytest.mark.usefixtures('public_room')
def test_client_already_on_the_room(server):
    room_code = '1'
    addr = ('127.0.0.1', 6000)

    server.parse_server_message('REGISTER', ['Tester'], addr)
    server.parse_server_message('ENTER', [room_code], addr)
    
    response = server.parse_server_message('ENTER', [room_code], addr)
    assert response == 'Cliente já está na sala'


@pytest.mark.usefixtures('public_room')
def test_client_already_on_other_room(server):
    room_code = '2'
    addr = ('127.0.0.1', 2000)  # usa o TestUser do public_room fixture

    server.parse_server_message('REGISTER', ['Tester'], ('127.0.0.1', 6000))
    server.parse_server_message('ROOM', ['pub', 'Room', 'Test'], ('127.0.0.1', 6000))

    response = server.parse_server_message('ENTER', [room_code], addr)
    assert response == 'Cliente já está em outra sala'


@pytest.mark.usefixtures('private_room')
def test_when_no_password_is_provided(server):
    room_code = '1'
    addr = ('127.0.0.1', 6000)

    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ENTER', [room_code], addr)
    assert response == 'Senha não fornecida'


@pytest.mark.usefixtures('private_room')
def test_when_password_is_incorrect(server):
    room_code = '1'
    addr = ('127.0.0.1', 6000)

    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ENTER', [room_code, 'wrongpass'], addr)
    assert response == 'Senha da sala está incorreta'


@pytest.mark.usefixtures('private_room')
def test_enter_private_room(server):
    room_code = '1'
    addr = ('127.0.0.1', 6000)

    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ENTER', [room_code, 'password'], addr)
    assert response == 'OK'
    assert server.clients[1]['room'] == room_code


@pytest.mark.usefixtures('public_room')
def test_enter_public_room(server):
    room_code = '1'
    addr = ('127.0.0.1', 6000)

    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('ENTER', [room_code], addr)
    assert response == 'OK'
    assert server.clients[1]['room'] == room_code


@pytest.mark.usefixtures('public_room')
def test_enter_non_lobby_room(server):
    room_code = '1'
    addr = ('127.0.0.1', 6000)

    server.parse_server_message('REGISTER', ['Tester'], addr)
    server.rooms[0]['state'] = 'game'

    response = server.parse_server_message('ENTER', [room_code], addr)
    assert response == 'A sala não está disponível'
    assert len(server.rooms[0]['clients']) == 1
    assert server.clients[1]['room'] is None


@pytest.mark.usefixtures('public_room')
def test_close_room_on_max_clients(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    server.rooms[0]['max_clients'] = 2
    
    server.parse_server_message('ENTER', ['1'], addr)
    assert server.rooms[0]['state'] == 'game'


def test_send_connect_message_to_clients(server):
    room_code = '1'

    addr1 = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester1'], addr1)
    server.parse_server_message('ROOM', ['pub', 'Room', 'Test'], addr1)

    addr2 = ('127.0.0.1', 6001)
    server.parse_server_message('REGISTER', ['Tester2'], addr2)


    response = server.parse_server_message('ENTER', [room_code], addr2)
    assert response == 'OK'
    assert len(server.rooms[0]['clients']) == 2

    message_0, addr_0 = server.socket.sendto_calls[0]
    message_1, addr_1 = server.socket.sendto_calls[1]
    assert message_0.startswith(b'/CONNECT:')
    assert addr_0 == addr1

    assert message_1.startswith(b'/CONNECT:')
    assert addr_1 == addr2
