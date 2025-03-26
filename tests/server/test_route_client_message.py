def test_valid_destination(server):
    server.clients = [
        {'id': 'client1', 'address': '127.0.0.1', 'port': 5000, 'room': 'room1'},
        {'id': 'client2', 'address': '127.0.0.2', 'port': 5001, 'room': 'room1'}
    ]

    server.rooms = [
        {
            'code': 'room1',
            'clients': [
                ('client1', '127.0.0.1', 5000),
                ('client2', '127.0.0.2', 5001)
            ]
        }
    ]

    address = (server.clients[0]['address'], server.clients[0]['port'])
    dest = 'client2'
    msg_type = 'TEST'
    args = ['test']


    response = server.routes_client_message(dest, msg_type, args, address)
    assert response is None

    expected_calls = [
        (
            f'{server.clients[0]['id']}/{msg_type}:{args[0]}'.encode(),
            (server.clients[1]['address'], server.clients[1]['port'])
        )
    ]
    assert server.socket.sendto_calls == expected_calls


def test_client_not_registered(server):
    address = ('127.0.0.1', 5000)
    dest = 'client2'
    msg_type = 'TEST'
    args = ['test']

    response = server.routes_client_message(dest, msg_type, args, address)
    assert response == 'Cliente não registrado'
    assert len(server.socket.sendto_calls) == 0


def test_client_not_in_any_room(server):
    server.clients = [
        {'id': 'client1', 'address': '127.0.0.1', 'port': 5000, 'room': ''}
    ]

    address = ('127.0.0.1', 5000)
    dest = 'client2'
    msg_type = 'TEST'
    args = ['test']


    response = server.routes_client_message(dest, msg_type, args, address)
    assert response == 'Cliente não está em nenhuma sala'
    assert len(server.socket.sendto_calls) == 0


def test_destination_not_found(server):
    server.clients = [
        {'id': 'client1', 'address': '127.0.0.1', 'port': 5000, 'room': 'room1'}
    ]

    server.rooms = [
        {
            'code': 'room1',
            'clients': [
                ('client1', '127.0.0.1', 5000)
            ]
        }
    ]

    address = ('127.0.0.1', 5000)
    dest = 'client2'
    msg_type = 'TEST'
    args = ['test']


    response = server.routes_client_message(dest, msg_type, args, address)
    assert response == 'Cliente destino não encontrado'
    assert len(server.socket.sendto_calls) == 0


def test_no_send_to_self(server):
    server.clients = [
        {'id': 'client1', 'address': '127.0.0.1', 'port': 5000, 'room': 'room1'}
    ]

    server.rooms = [
        {
            'code': 'room1',
            'clients': [
                ('client1', '127.0.0.1', 5000)
            ]
        }
    ]

    address = ('127.0.0.1', 5000)
    dest = 'client1'
    msg_type = 'TEST'
    args = ['test']


    response = server.routes_client_message(dest, msg_type, args, address)
    assert response == 'Cliente destino é o próprio cliente'
    assert len(server.socket.sendto_calls) == 0
