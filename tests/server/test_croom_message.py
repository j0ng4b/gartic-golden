def test_complain_about_client_unregistred(server):
    addr = ('127.0.0.1', 6000)

    response = server.parse_server_message('CROOM', [], addr)
    assert response == 'Cliente não registrado'


def test_complain_about_extra_arguments(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('CROOM', ['extra'], addr)
    assert response == 'Número de argumentos inválido'


def test_client_not_on_any_room(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    response = server.parse_server_message('CROOM', [], addr)
    assert response == 'Cliente não está em nenhuma sala'


def test_only_owner_can_close_room(server):
    addr1 = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester1'], addr1)
    server.parse_server_message('ROOM', ['pub', 'TestRoom', 'Test'], addr1)

    addr2 = ('127.0.0.1', 6001)
    server.parse_server_message('REGISTER', ['Tester2'], addr2)
    server.parse_server_message('ENTER', ['1'], addr2)

    response = server.parse_server_message('CROOM', [], addr2)
    assert response == 'Somente o dono da sala pode fechá-la'


def test_close_room(server):
    addr1 = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester1'], addr1)
    server.parse_server_message('ROOM', ['pub', 'TestRoom', 'Test'], addr1)

    addr2 = ('127.0.0.1', 6001)
    server.parse_server_message('REGISTER', ['Tester2'], addr2)
    server.parse_server_message('ENTER', ['1'], addr2)

    response = server.parse_server_message('CROOM', [], addr1)
    assert response == 'OK'
    assert server.rooms[0]['state'] == 'game'


def test_send_play_and_game_messages_to_clients(server):
    addr1 = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester1'], addr1)
    server.parse_server_message('ROOM', ['pub', 'TestRoom', 'Test'], addr1)

    addr2 = ('127.0.0.1', 6001)
    server.parse_server_message('REGISTER', ['Tester2'], addr2)
    server.parse_server_message('ENTER', ['1'], addr2)
    server.socket.sendto_calls.clear()

    response = server.parse_server_message('CROOM', [], addr1)
    assert response == 'OK'
    assert server.rooms[0]['state'] == 'game'

    expected_calls = [
        (f'/PLAY:'.encode(), addr2),
        (f'/GAME:'.encode(), addr1),
    ]
    assert server.socket.sendto_calls == expected_calls


def test_close_room_with_few_clients(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)
    server.parse_server_message('ROOM', ['pub', 'TestRoom', 'Test'], addr)

    response = server.parse_server_message('CROOM', [], addr)
    assert response == 'Poucos clientes na sala'
    assert server.rooms[0]['state'] == 'lobby'
