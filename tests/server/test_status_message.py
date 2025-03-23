def test_complain_about_client_unregistred(server):
    addr = ('127.0.0.1', 6001)

    response = server.parse_message('STATUS', [], addr)
    assert response == 'Cliente não registrado'


def test_complain_about_extra_arguments(server):
    addr = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Big Smoke'], addr)

    response = server.parse_message('STATUS', ['arg'], addr)
    assert response == 'Número de argumentos inválido'


def test_when_client_not_on_any_room(server):
    addr = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Big Smoke'], addr)

    response = server.parse_message('STATUS', [], addr)
    assert response == 'Cliente não está em nenhuma sala'


def test_output_format(server):
    addr = ('127.0.0.1', 6001)
    server.parse_message('REGISTER', ['Pikachu'], addr)

    room_code = '1'
    server.rooms = [{
         'name': 'TestRoom',
         'code': room_code,
         'password': None,
         'max_clients': 10,
         'clients': [addr]
    }]

    client = server.get_client(addr[0], addr[1])
    server.clients[client]['room'] = room_code

    response = server.parse_message('STATUS', [], addr)
    assert response == f'pub,TestRoom,{room_code},1,10'


