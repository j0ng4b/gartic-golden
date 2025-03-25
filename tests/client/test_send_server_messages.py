def test_register_success(client):
    def dummy_send_message(type, *args, dest='', wait_response=True):
        return 'OK'
    client.send_message = dummy_send_message

    response = client.server_register()
    assert response is True


def test_register_failure(client):
    def dummy_send_message(type, *args, dest='', wait_response=True):
        return 'ERROR'
    client.send_message = dummy_send_message

    response = client.server_register()
    assert response is False


def test_unregister_success(client):
    def dummy_send_message(type, *args, dest='', wait_response=True):
        return 'OK'
    client.send_message = dummy_send_message

    response = client.server_unregister()
    assert response is True


def test_unregister_failure(client):
    def dummy_send_message(type, *args, dest='', wait_response=True):
        return 'ERROR'
    client.send_message = dummy_send_message

    response = client.server_unregister()
    assert response is False


def test_create_room_success(client):
    def dummy_send_message(type, *args, dest='', wait_response=True):
        return '123'
    client.send_message = dummy_send_message

    response = client.server_create_room('pub', 'room1')
    assert response is True
    assert client.room == '123'


def test_create_room_failure(client):
    def dummy_send_message(type, *args, dest='', wait_response=True):
        return 'ERROR'
    client.send_message = dummy_send_message

    response = client.server_create_room('pub', 'room1')
    assert response is False
    assert client.room is None


def test_close_room_success(client):
    client.room = '123'

    def dummy_send_message(type, *args, dest='', wait_response=True):
        return 'OK'
    client.send_message = dummy_send_message

    response = client.server_close_room()
    assert response is True
    assert client.room is None


def test_close_room_failure(client):
    client.room = '123'

    def dummy_send_message(type, *args, dest='', wait_response=True):
        return 'ERROR'
    client.send_message = dummy_send_message

    response = client.server_close_room()
    assert response is False
    assert client.room is not None


def test_leave_room_success(client):
    client.room = '123'
    client.room_clients = {('127.0.0.1', 8000): {'name': 'Client', 'address': ('127.0.0.1', 8000), 'msgs': []}}

    def dummy_send_message(type, *args, dest='', wait_response=True):
        return 'OK'
    client.send_message = dummy_send_message

    response = client.server_leave_room()
    assert response is True
    assert client.room is None
    assert client.room_clients == {}


def test_enter_room_success(client):
    def dummy_send_message(type, *args, dest='', wait_response=True):
        return 'OK'
    client.send_message = dummy_send_message

    response = client.server_enter_room('123')
    assert response is True
    assert client.room == '123'


def test_enter_room_failure(client):
    def dummy_send_message(type, *args, dest='', wait_response=True):
        return 'FAILED'
    client.send_message = dummy_send_message

    response = client.server_enter_room('123')
    assert response is False
    assert client.room is None


def test_list_rooms(client):
    def dummy_send_message(type, *args, dest='', wait_response=True):
        return 'room1\nroom2\nroom3'
    client.send_message = dummy_send_message

    rooms = client.server_list_rooms()
    assert rooms == ['room1', 'room2', 'room3']


def test_status_room(client, caplog):
    def dummy_send_message(type, *args, dest='', wait_response=True):
        return 'STATUS'
    client.send_message = dummy_send_message

    response = client.server_status_room()
    assert response == 'STATUS'

