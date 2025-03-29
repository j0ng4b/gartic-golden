def test_invalid_client(client):
    dest = 'client2'

    response = client.parse_client_message(dest, 'SCORE', [])
    assert response == 'Cliente não encontrado'


def test_returning_score(client):
    dest = 'client2'

    client.room_clients[dest] = {
        'name': 'TestClient',
        'msgs': [],
        'state': None,
        'score': 0
    }

    assert client.parse_client_message(dest, 'SCORE', []) == 0

