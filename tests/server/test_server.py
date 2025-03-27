def test_get_invalid_client(server):
    addr = ('127.0.0.1', 6000)
    assert server.get_client(addr[0], addr[1]) is None


def test_get_valid_client(server):
    addr = ('127.0.0.1', 6000)
    server.parse_server_message('REGISTER', ['Tester'], addr)

    client = server.get_client(addr[0], addr[1])
    assert client is not None
    assert client['name'] == 'Tester'


def test_get_invalid_room(server):
    room_code = '1'
    assert server.get_room(room_code) is None


def test_get_valid_room(server):
    room_code = '1'
    server.rooms = [{
        'name': 'TestRoom',
        'code': room_code,
        'password': None,
        'max_clients': 10,
        'clients': []
    }]

    room = server.get_room(room_code)
    assert room is not None
    assert room['name'] == 'TestRoom'
    assert room['code'] == room_code
    assert room['password'] is None
    assert room['max_clients'] == 10


def test_parse_valid_messages_types(server):
    addr = ('127.0.0.1', 6000)

    test_table = [
        'REGISTER',
        'UNREGISTER',
        'ROOM',
        'CROOM',
        'LIST',
        'ENTER',
        'LEAVE',
        'END',
    ]

    for msg_type in test_table:
        response = server.parse_server_message(msg_type, [], addr)
        assert response != 'Tipo de mensagem inválido'


def test_parse_invalid_messages_types(server):
    addr = ('127.0.0.1', 6000)

    response = server.parse_server_message('register', [], addr)
    assert response == 'Tipo de mensagem inválido'

    response = server.parse_server_message('Register', [], addr)
    assert response == 'Tipo de mensagem inválido'

    response = server.parse_server_message('Invalid', [], addr)
    assert response == 'Tipo de mensagem inválido'
