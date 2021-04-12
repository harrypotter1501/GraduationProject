# test fixture

import os
import tempfile

import pytest

from flaskr import create_app
from flaskr.db import get_db, init_db

import socket


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        #get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# authorization actions
class AuthActions(object):
    ''' management of user-login '''

    def __init__(self, client):
        self._client = client

    def login(self, code='test'):
        return self._client.get(
            'http://127.0.0.1:5000/login/?code={}'.format(code)
        )

    def logout(self):
        return self._client.get('/auth/logout/')


@pytest.fixture
def auth(client):
    return AuthActions(client)


# device actions
class DeviceActions(object):
    ''' management of device login '''

    def __init__(self, client, socket_enabled):
        self._client = client
        self._socket = socket.socket()

    def send_text(self):
        self._socket.send(b'some text')

    def login(self, device_id='test', device_key='123456'):
        rv = self._client.get(
            'http://127.0.0.1:5000/device/?device_id={}&device_key={}'.format(device_id, device_key)
        )

        self._socket.connect(('127.0.0.1', 6000))

        data = self._socket.recv(1024).decode()
        assert 'established' in data

        return rv

    def logout(self, client):
        pass


@pytest.fixture
def dev(client, socket_enabled):
    return DeviceActions(client, socket_enabled)
