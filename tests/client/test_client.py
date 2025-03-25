def test_send_message(client):
    response = client.send_message('TEST', 'arg1', 'arg2', wait_response=False)
    assert client.socket.send_calls[-1] == b'/TEST:arg1;arg2'
    assert response is None


def test_get_message(client):
    client.msgs = ['Message1', 'Message2']

    msg = client.get_message()
    assert msg == 'Message1'

    msg2 = client.get_message()
    assert msg2 == 'Message2'

