def test_register_chat_message(client):
    dest = 'client2'
    client.room_clients[dest] = {'name': 'TestClient', 'msgs': []}

    client.parse_client_message(dest, 'CHAT', ['Hello'])
    assert 'Hello' in client.room_clients[dest]['msgs']

    assert len(client.handle_chat_calls) == 1
    assert client.handle_chat_calls[-1][1] == 'Hello'


def test_invalid_client(client):
    dest = 'client2'

    client.parse_client_message(dest, 'CHAT', ['Hello'])
    assert len(client.handle_chat_calls) == 0

