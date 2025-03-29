def test_invalid_client(client):
    dest = 'client2'

    response = client.parse_client_message(dest, 'SKIP', [])
    assert response == 'Cliente não encontrado'


def test_already_skipped(client):
    dest = 'client2'
    client.room_clients[dest] = {'name': 'TestClient', 'msgs': [], 'state': 'skip'}

    response = client.parse_client_message(dest, 'SKIP', [])
    assert response == 'Cliente já não pode mais dar palpites'


def test_when_guessed(client):
    dest = 'client2'
    client.room_clients[dest] = {'name': 'TestClient', 'msgs': [], 'state': 'guess'}

    response = client.parse_client_message(dest, 'SKIP', [])
    assert response == 'Cliente já acertou o palpite'


def test_when_drawing(client):
    dest = 'client2'
    client.room_clients[dest] = {'name': 'TestClient', 'msgs': [], 'state': 'draw'}

    response = client.parse_client_message(dest, 'SKIP', [])
    assert response == 'Cliente é quem está desenhando'


def test_skip(client):
    dest = 'client2'

    client.room_clients[dest] = {
        'name': 'TestClient',
        'msgs': [],
        'state': None,
        'score': 0
    }

    response = client.parse_client_message(dest, 'SKIP', [])
    assert response == 'OK'

    assert client.room_clients[dest]['state'] == 'skip'
    assert client.room_clients[dest]['score'] == 0

