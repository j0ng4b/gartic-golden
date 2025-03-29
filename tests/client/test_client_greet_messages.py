def test_parse_greet_message(client):
    client.room_clients['client1'] = {'name': None, 'msgs': []}

    result = client.parse_client_message('client2', 'GREET', [])
    assert result == client.name

