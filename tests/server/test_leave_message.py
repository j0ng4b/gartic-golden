def test_complain_about_client_unregistred(server):
    addr = ('127.0.0.1', 8000)

    response = server.parse_message('LEAVE', [], addr)
    assert response == 'Cliente não registrado'


def test_complain_about_extra_arguments(server):
    addr = ('127.0.0.1', 8000)
    server.parse_message('REGISTER', ['Rider'], addr)

    response = server.parse_message('LEAVE', ['extra'], addr)
    assert response == 'Número de argumentos inválido'


def test_when_client_not_on_any_room(server):
    addr = ('127.0.0.1', 8000)
    server.parse_message('REGISTER', ['Rider'], addr)

    response = server.parse_message('LEAVE', [], addr)
    assert response == 'Cliente não está em nenhuma sala'


def test_leave_room(server):
    addr = ('127.0.0.1', 8000)
    server.parse_message('REGISTER', ['Rider'], addr)

    server.rooms = [{
        'name': 'TestRoom',
        'code': '1',
        'password': None,
        'max_clients': 10,
        'clients': []
    }]
    server.parse_message('ENTER', ['1'], addr)

    response = server.parse_message('LEAVE', [], addr)
    assert response == 'OK'

