def test_parse_client_message_greet(client):
    client.room_clients['client1'] = {'name': None, 'msgs': []}

    result = client.parse_client_message('client2', 'GREET', [])
    assert result == client.name


def test_parse_client_message_chat(client):
    dest = 'client2'
    client.room_clients[dest] = {'name': 'TestClient', 'msgs': []}

    client.parse_client_message(dest, 'CHAT', ['Hello'])
    assert 'Hello' in client.room_clients[dest]['msgs']
