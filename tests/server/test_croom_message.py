def test_complain_about_client_unregistred(server):
    addr = ('127.0.0.1', 6001)

    response = server.parse_message('CROOM', ['1'], addr)
    assert response == 'Cliente não registrado'


def test_complain_about_extra_arguments(server):
    addr = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Donkey'], addr)

    response = server.parse_message('CROOM', ['1', 'Kong'], addr)
    assert response == 'Número de argumentos inválido'


def test_invalid_room_code(server):
    addr = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Donkey'], addr)

    response = server.parse_message('CROOM', ['1'], addr)
    assert response == 'Código da sala inválido'


def test_only_owner_can_close_room(server):
    addr1 = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Donkey'], addr1)
    server.parse_message('ROOM', ['pub', 'RoomOne'], addr1)

    addr = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Kong'], addr)

    response = server.parse_message('CROOM', ['1'], addr)
    assert response == 'Somente o dono da sala pode fechá-la'


def test_close_room(server):
    addr = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Donkey'], addr)
    server.parse_message('ROOM', ['pub', 'RoomOne'], addr)

    response = server.parse_message('CROOM', ['1'], addr)
    assert response == 'OK'

