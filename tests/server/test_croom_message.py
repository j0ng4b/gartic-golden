def test_complain_about_client_unregistred(server):
    addr = ('127.0.0.1', 6001)

    response = server.parse_message('CROOM', [], addr)
    assert response == 'Cliente não registrado'


def test_complain_about_extra_arguments(server):
    addr = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Donkey'], addr)

    response = server.parse_message('CROOM', ['NoProblem'], addr)
    assert response == 'Número de argumentos inválido'


def test_client_not_on_any_room(server):
    addr = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Donkey'], addr)

    response = server.parse_message('CROOM', [], addr)
    assert response == 'Cliente não está em nenhuma sala'


def test_only_owner_can_close_room(server):
    addr1 = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Donkey'], addr1)
    server.parse_message('ROOM', ['pub', 'RoomOne'], addr1)

    addr = ('127.0.0.1', 6002)
    server.parse_message('REGISTER', ['Kong'], addr)
    server.parse_message('ENTER', ['1'], addr)

    response = server.parse_message('CROOM', [], addr)
    assert response == 'Somente o dono da sala pode fechá-la'


def test_close_room(server):
    addr = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Donkey'], addr)
    server.parse_message('ROOM', ['pub', 'RoomOne'], addr)

    response = server.parse_message('CROOM', [], addr)
    assert response == 'OK'

