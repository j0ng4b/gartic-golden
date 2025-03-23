def test_complain_about_extra_arguments(server):
    addr = ('127.0.0.1', 5000)
    server.parse_message('REGISTER', ['Alice'], addr)

    response = server.parse_message('UNREGISTER', ['extra'], addr)
    assert response == 'Número de argumentos inválido'


def test_error_on_client_unregistred(server):
    addr = ('127.0.0.1', 5000)

    response = server.parse_message('UNREGISTER', [], addr)
    assert response == 'Cliente não registrado'


def test_success_unregister(server):
    addr = ('127.0.0.1', 5000)
    server.parse_message('REGISTER', ['Alice'], addr)

    response = server.parse_message('UNREGISTER', [], addr)
    assert response == 'OK'
    assert not any(client['name'] == 'Alice' for client in server.clients)

