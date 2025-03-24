def test_send_message(client):
    response = client.send_message('TEST', 'arg1', 'arg2', wait_response=False)
    assert client.socket.sendto_calls[-1] == (b'TEST:arg1;arg2', client.address)
    assert response is None


def test_get_message(client):
    client.msgs[client.address] = ['Message1', 'Message2']

    msg = client.get_message(client.address)
    assert msg == 'Message1'

    msg2 = client.get_message(client.address)
    assert msg2 == 'Message2'

