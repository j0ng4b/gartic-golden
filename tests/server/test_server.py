def test_get_invalid_client(server):
    addr = ('127.0.0.1', 5008)
    assert server.get_client(addr[0], addr[1]) is None


def test_get_valid_client(server):
    addr = ('127.0.0.1', 5008)
    server.parse_server_message('REGISTER', ['Grace'], addr)

    client = server.get_client(addr[0], addr[1])
    assert client is not None
    assert client['name'] == 'Grace'


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

