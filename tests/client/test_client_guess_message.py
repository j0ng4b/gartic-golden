def test_invalid_client(client):
    dest = 'client2'

    response = client.parse_client_message(dest, 'GUESS', ['ball'])
    assert response == 'Cliente não encontrado'


def test_already_guessed(client):
    dest = 'client2'
    client.room_clients[dest] = {'name': 'TestClient', 'msgs': [], 'state': 'guess'}

    response = client.parse_client_message(dest, 'GUESS', ['ball'])
    assert response == 'Palpite já foi dado'


def test_when_skipped(client):
    dest = 'client2'
    client.room_clients[dest] = {'name': 'TestClient', 'msgs': [], 'state': 'skip'}

    response = client.parse_client_message(dest, 'GUESS', ['ball'])
    assert response == 'Cliente não pode mais dar palpites'


def test_when_drawing(client):
    dest = 'client2'
    client.room_clients[dest] = {'name': 'TestClient', 'msgs': [], 'state': 'draw'}

    response = client.parse_client_message(dest, 'GUESS', ['ball'])
    assert response == 'Cliente é quem está desenhando'


def test_wrong_guess(client):
    dest = 'client2'

    client.draw_object = 'cat'
    client.room_clients[dest] = {'name': 'TestClient', 'msgs': [], 'state': None}

    response = client.parse_client_message(dest, 'GUESS', ['ball'])
    assert response == 'Palpite está incorreto'


def test_correct_guess(client):
    dest = 'client2'

    client.draw_object = 'cat'
    client.room_clients[dest] = {
        'name': 'TestClient',
        'msgs': [],
        'state': None,
        'score': 0
    }

    response = client.parse_client_message(dest, 'GUESS', ['cat'])
    assert response == 'OK'

    assert client.room_clients[dest]['state'] == 'guess'
    assert client.room_clients[dest]['score'] == 5


def test_send_gtra_on_correct_guess(client):
    dest1 = 'client2'
    dest2 = 'client3'

    client.draw_object = 'cat'
    client.room_clients[dest1] = {
        'name': 'TestClient1',
        'msgs': [],
        'state': None,
        'score': 0
    }

    client.room_clients[dest2] = {
        'name': 'TestClient2',
        'msgs': [],
        'state': None,
        'score': 0
    }

    client.parse_client_message(dest1, 'GUESS', ['cat'])
    assert len(client.socket.send_calls) == 1
    assert client.socket.send_calls == [b'client3/GTRA:client2']
