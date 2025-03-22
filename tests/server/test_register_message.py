def test_complain_about_extra_arguments(server):
    addr = ('127.0.0.1', 5000)

    response = server.parse_message('REGISTER', [], addr)
    assert response == 'Número de argumentos inválido'


def test_wrong_client_name(server):
    addr = ('127.0.0.1', 5000)

    response = server.parse_message('REGISTER', [''], addr)
    assert response == 'Nome de jogador inválido'


def test_success_registred(server):
    addr = ('127.0.0.1', 5000)

    response = server.parse_message('REGISTER', ['Alice'], addr)
    assert response == 'OK'
    assert any(client['name'] == 'Alice' for client in server.clients)

