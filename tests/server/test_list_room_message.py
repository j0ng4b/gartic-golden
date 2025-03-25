import pytest


@pytest.fixture
def rooms(server):
    addr1 = ('127.0.0.1', 5005)
    server.parse_server_message('REGISTER', ['Eve'], addr1)
    server.parse_server_message('ROOM', ['pub', 'RoomOne'], addr1)

    addr2 = ('127.0.0.1', 5006)
    server.parse_server_message('REGISTER', ['Frank'], addr2)
    server.parse_server_message('ROOM', ['priv', 'RoomTwo', 'secret'], addr2)


def test_iniaially_empty_list(server):
    addr = ('127.0.0.1', 5007)

    response = server.parse_server_message('LIST', [], addr)
    assert response == ''


@pytest.mark.usefixtures('rooms')
def test_list_return_all_rooms(server):
    addr = ('127.0.0.1', 5007)

    response = server.parse_server_message('LIST', [], addr)
    lines = response.strip().split('\n')
    assert len(lines) == 2


@pytest.mark.usefixtures('rooms')
def test_list_return_public_rooms(server):
    addr = ('127.0.0.1', 5007)

    response = server.parse_server_message('LIST', ['pub'], addr)
    lines = [line for line in response.strip().split('\n') if line]
    assert len(lines) == 1
    assert 'RoomOne' in lines[0]


@pytest.mark.usefixtures('rooms')
def test_list_return_private_rooms(server):
    addr = ('127.0.0.1', 5007)

    response = server.parse_server_message('LIST', ['priv'], addr)
    lines = [line for line in response.strip().split('\n') if line]
    assert len(lines) == 1
    assert 'RoomTwo' in lines[0]

