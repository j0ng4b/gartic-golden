def test_parse_client_message_greet(client):
    key = ('127.0.0.1', 8083)
    client.room_clients[key] = {'name': None, 'address': key, 'msgs': []}

    result = client.parse_client_message('GREET', [], key)
    assert result == client.name


def test_parse_client_message_chat(client):
    key = ('127.0.0.1', 8084)
    client.room_clients[key] = {'name': 'TestClient', 'address': key, 'msgs': []}

    client.parse_client_message('CHAT', ['Hello'], key)

    assert 'Hello' in client.room_clients[key]['msgs']
    assert 'Hello' in client.room_clients[key].get('handled_chats', [])

