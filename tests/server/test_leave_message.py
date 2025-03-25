def test_complain_about_client_unregistred(server):
    addr = ('127.0.0.1', 8000)

    response = server.parse_server_message('LEAVE', [], addr)
    assert response == 'Cliente não registrado'


def test_complain_about_extra_arguments(server):
    addr = ('127.0.0.1', 8000)
    server.parse_server_message('REGISTER', ['Rider'], addr)

    response = server.parse_server_message('LEAVE', ['extra'], addr)
    assert response == 'Número de argumentos inválido'


def test_when_client_not_on_any_room(server):
    addr = ('127.0.0.1', 8000)
    server.parse_server_message('REGISTER', ['Rider'], addr)

    response = server.parse_server_message('LEAVE', [], addr)
    assert response == 'Cliente não está em nenhuma sala'


def test_leave_room(server):
    addr = ('127.0.0.1', 8000)
    server.parse_server_message('REGISTER', ['Rider'], addr)

    server.rooms = [{
        'name': 'TestRoom',
        'code': '1',
        'password': None,
        'max_clients': 10,
        'clients': []
    }]
    server.parse_server_message('ENTER', ['1'], addr)

    response = server.parse_server_message('LEAVE', [], addr)
    assert response == 'OK'

def test_send_disconnect_message_to_clients(server):
    addr1 = ('127.0.0.1', 6004)
    server.parse_server_message('REGISTER', ['Snoopy'], addr1)
    room_code = server.parse_server_message('ROOM', ['pub', 'Room'], addr1)

    addr2 = ('127.0.0.1', 6003)
    server.parse_server_message('REGISTER', ['Charlie Brown'], addr2)
    server.parse_server_message('ENTER', [room_code], addr2)
    server.socket.sendto_calls.clear()

    response = server.parse_server_message('LEAVE', [], addr2)
    assert response == 'OK'

    expected_calls = [
        (f'DISCONNECT:{addr2[0]};{addr2[1]}'.encode(), addr1),
    ]
    assert server.socket.sendto_calls == expected_calls

