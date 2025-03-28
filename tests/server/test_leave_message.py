import pytest


@pytest.fixture
def room(server):
    addr = ('127.0.0.1', 2000)
    server.parse_server_message('REGISTER', ['TestUser'], addr)
    server.parse_server_message('ROOM', ['pub', 'TestRoom', 'Test'], addr)



def test_complain_about_client_unregistred(server):
    addr = ('127.0.0.1', 6000)

    response = server.parse_server_message('LEAVE', [], addr)
    assert response == 'Cliente não registrado'


def test_complain_about_extra_arguments(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('LEAVE', ['extra'], addr)
    assert response == 'Número de argumentos inválido'


def test_when_client_not_on_any_room(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('LEAVE', [], addr)
    assert response == 'Cliente não está em nenhuma sala'


@pytest.mark.usefixtures('room')
def test_leave_room(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)
    server.parse_server_message('ENTER', ['1'], addr)

    response = server.parse_server_message('LEAVE', [], addr)
    assert response == 'OK'
    assert len(server.rooms[0]['clients']) == 1
    assert server.clients[1]['room'] is None


@pytest.mark.usefixtures('room')
def test_remove_room_when_last_client_leaves(server):
    addr = ('127.0.0.1', 2000)  # usa o TestUser do room fixture

    response = server.parse_server_message('LEAVE', [], addr)
    assert response == 'OK'
    assert len(server.rooms) == 0


@pytest.mark.usefixtures('room')
def test_send_disconnect_message_to_clients(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)
    server.parse_server_message('ENTER', ['1'], addr)
    server.socket.sendto_calls.clear()

    response = server.parse_server_message('LEAVE', [], addr)
    assert response == 'OK'
    assert len(server.rooms[0]['clients']) == 1

    message, addr = server.socket.sendto_calls[0]
    assert message.startswith(b'/DISCONNECT:')
    assert addr == ('127.0.0.1', 2000)  # usa o TestUser do room fixture
