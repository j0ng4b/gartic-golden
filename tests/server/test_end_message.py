def test_complain_about_client_unregistred(server):
    addr = ('127.0.0.1', 6000)

    response = server.parse_server_message('END', [], addr)
    assert response == 'Cliente não registrado'


def test_complain_about_extra_arguments(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('END', ['extra'], addr)
    assert response == 'Número de argumentos inválido'


def test_client_not_on_any_room(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('END', [], addr)
    assert response == 'Cliente não está em nenhuma sala'


def test_only_owner_can_remove_room(server):
    addr1 = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester1'], addr1)
    server.parse_server_message('ROOM', ['pub', 'TestRoom', 'Test'], addr1)

    addr2 = ('127.0.0.1', 6001)
    server.parse_server_message('REGISTER', ['Tester2'], addr2)
    server.parse_server_message('ENTER', ['1'], addr2)

    response = server.parse_server_message('END', [], addr2)
    assert response == 'Somente o dono da sala pode excluí-la'


def test_end_room(server):
    addr1 = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester1'], addr1)
    server.parse_server_message('ROOM', ['pub', 'TestRoom', 'Test'], addr1)

    addr2 = ('127.0.0.1', 6001)
    server.parse_server_message('REGISTER', ['Tester2'], addr2)
    server.parse_server_message('ENTER', ['1'], addr2)
    server.parse_server_message('CROOM', [], addr1)

    response = server.parse_server_message('END', [], addr1)
    assert response == 'OK'
    assert len(server.rooms) == 0


def test_send_end_message_to_clients(server):
    addr1 = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester1'], addr1)
    server.parse_server_message('ROOM', ['pub', 'TestRoom', 'Test'], addr1)

    addr2 = ('127.0.0.1', 6001)
    server.parse_server_message('REGISTER', ['Tester2'], addr2)
    server.parse_server_message('ENTER', ['1'], addr2)
    server.parse_server_message('CROOM', [], addr1)
    server.socket.sendto_calls.clear()

    server.parse_server_message('END', [], addr1)
    assert server.socket.sendto_calls == [(f'/END:'.encode(), addr2)]


def test_end_not_in_game_room(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)
    server.parse_server_message('ROOM', ['pub', 'TestRoom', 'Test'], addr)

    response = server.parse_server_message('END', [], addr)
    assert response == 'A sala não está em partida'

