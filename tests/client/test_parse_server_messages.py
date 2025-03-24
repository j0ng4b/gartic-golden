def test_parse_server_message_connect(client):
    def dummy_send_message(type, *args, address=None, wait_response=True):
        return 'GREET_PLAYER'
    client.send_message = dummy_send_message

    args = ['127.0.0.1', '8081']
    client.parse_server_message('CONNECT', args)

    key = ('127.0.0.1', 8081)
    assert key in client.msgs
    assert client.msgs[key] == []
    assert key in client.room_clients
    assert client.room_clients[key]['name'] == 'GREET_PLAYER'


def test_parse_server_message_disconnect(client):
    key = ('127.0.0.1', 8082)

    client.msgs[key] = ['something']
    client.room_clients[key] = {'name': 'Test', 'address': key, 'msgs': []}

    args = ['127.0.0.1', '8082']
    client.parse_server_message('DISCONNECT', args)

    assert key not in client.msgs
    assert key not in client.room_clients

