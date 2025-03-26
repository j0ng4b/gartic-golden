def test_parse_server_message_connect(client):
    def dummy_send_message(type, *args, dest='', wait_response=True):
        return 'GREET_PLAYER'
    client.send_message = dummy_send_message


    client.parse_server_message('CONNECT', ['client2'])
    assert 'client2' in client.room_clients
    assert client.msgs['client2'] == []
    assert client.room_clients['client2']['name'] == 'GREET_PLAYER'


def test_parse_server_message_disconnect(client):
    client.msgs['client2'] = []
    client.room_clients['client2'] = {'name': 'Test', 'msgs': []}

    client.parse_server_message('DISCONNECT', ['client2'])
    assert 'client2' not in client.room_clients
    assert len(client.room_clients) == 0

