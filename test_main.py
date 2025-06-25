from tempfile import NamedTemporaryFile

import pytest
from fastapi.testclient import TestClient

import hosts_repository
from main import app


test_db = NamedTemporaryFile(delete=False)
hosts_repository.init(test_db.name)

client = TestClient(app)

this_guy: dict = None
other_guy: dict = None


@pytest.fixture(scope='session')
def close_hosts():
    yield
    test_db.close()


def test_create():
    global this_guy, other_guy

    response = client.post(f'/testee')
    assert response.status_code == 200
    this_guy = {
        'uuid': 'TESTEE',
        'only_friends': True,
        'allow_nonames': False,
        'friends': [],
        'banlist': []
    }
    assert response.json() == this_guy, (response.json(), this_guy)

    response = client.post(f'/testee')
    assert response.status_code == 409

    other_guy = client.post(f'/other_guy').json()


def test_get():
    global this_guy

    assert client.get(f'/{this_guy['uuid']}').json() == this_guy
    assert client.get('/bad_test').status_code == 404


def test_not_welcomes_noname():
    assert client.get(f'/{this_guy['uuid']}/welcomes/NONAME').status_code == 404


def test_not_welcomes_not_friend():
    assert client.get(f'/{this_guy['uuid']}/welcomes/{other_guy['uuid']}').status_code == 404


def test_befriend():
    global this_guy

    assert client.post(
        f'/{this_guy['uuid']}/friends/{other_guy['uuid']}'
    ).status_code == 200
    this_guy['friends'].append(other_guy['uuid'])
    assert client.get(f'/{this_guy['uuid']}').json() == this_guy

    not_exists_this = client.post(f'/noone/friends/{other_guy['uuid']}')
    assert not_exists_this.status_code == 404
    assert not_exists_this.json()['message'] == 'not found this'

    not_exists_other = client.post(f'/{this_guy['uuid']}/friends/noone')
    assert not_exists_other.status_code == 404
    assert not_exists_other.json()['message'] == 'not found other'


def test_welcomes_friend():
    assert client.get(f'/{this_guy['uuid']}/welcomes/NONAME').status_code == 404
    assert client.get(f'/{this_guy['uuid']}/welcomes/{other_guy['uuid']}').status_code == 200


def test_unfriend():
    global this_guy

    assert client.delete(
        f'/{this_guy['uuid']}/friends/{other_guy['uuid']}'
    ).status_code == 200
    this_guy['friends'].remove(other_guy['uuid'])
    assert client.get(f'/{this_guy['uuid']}').json() == this_guy

    not_exists_this = client.post(f'/noone/friends/{other_guy['uuid']}')
    assert not_exists_this.status_code == 404
    assert not_exists_this.json()['message'] == 'not found this'

    not_exists_other = client.post(f'/{this_guy['uuid']}/friends/noone')
    assert not_exists_other.status_code == 404
    assert not_exists_other.json()['message'] == 'not found other'


def test_not_welcomes_not_a_friend_anymore():
    assert client.get(f'/{this_guy['uuid']}/welcomes/{other_guy['uuid']}').status_code == 404


def test_set_only_friends():
    global this_guy

    assert client.put(
        f'/{this_guy['uuid']}/only_friends',
        json={'only_friends': False}
    ).status_code == 200
    assert client.put(
        '/bad_test/only_friends',
        json={'only_friends': False}
    ).status_code == 404

    this_guy['only_friends'] = False
    assert client.get(f'/{this_guy['uuid']}').json() == this_guy


def test_welcomes_not_a_friend_anymore():
    assert client.get(f'/{this_guy['uuid']}/welcomes/{other_guy['uuid']}').status_code == 200


def test_not_welcomes_NONAME():
    assert client.get(f'/{this_guy['uuid']}/welcomes/NONAME').status_code == 404


def test_set_allow_nonames():
    global this_guy

    assert client.put(
        f'/{this_guy['uuid']}/allow_nonames',
        json={'allow_nonames': True}
    ).status_code == 200
    assert client.put(
        '/bad_test/allow_nonames',
        json={'allow_nonames': True}
    ).status_code == 404

    this_guy['allow_nonames'] = True
    assert client.get(f'/{this_guy['uuid']}').json() == this_guy


def test_welcomes_NONAME():
    assert client.get(f'/{this_guy['uuid']}/welcomes/NONAME').status_code == 200


def test_ban():
    global this_guy

    assert client.post(
        f'/{this_guy['uuid']}/banlist/{other_guy['uuid']}'
    ).status_code == 200
    this_guy['banlist'].append(other_guy['uuid'])
    assert client.get(f'/{this_guy['uuid']}').json() == this_guy

    not_exists_this = client.post(f'/noone/banlist/{other_guy['uuid']}')
    assert not_exists_this.status_code == 404
    assert not_exists_this.json()['message'] == 'not found this'

    not_exists_other = client.post(f'/{this_guy['uuid']}/banlist/noone')
    assert not_exists_other.status_code == 404
    assert not_exists_other.json()['message'] == 'not found other'


def test_not_welcomes_banned_guy():
    assert client.get(f'/{this_guy['uuid']}/welcomes/{other_guy['uuid']}').status_code == 404


def test_unban():
    global this_guy

    assert client.delete(
        f'/{this_guy['uuid']}/banlist/{other_guy['uuid']}'
    ).status_code == 200
    this_guy['banlist'].remove(other_guy['uuid'])
    assert client.get(f'/{this_guy['uuid']}').json() == this_guy

    not_exists_this = client.post(f'/noone/banlist/{other_guy['uuid']}')
    assert not_exists_this.status_code == 404
    assert not_exists_this.json()['message'] == 'not found this'

    not_exists_other = client.post(f'/{this_guy['uuid']}/banlist/noone')
    assert not_exists_other.status_code == 404
    assert not_exists_other.json()['message'] == 'not found other'


def test_welcomes_not_anymore_banned_guy():
    assert client.get(f'/{this_guy['uuid']}/welcomes/{other_guy['uuid']}').status_code == 200
