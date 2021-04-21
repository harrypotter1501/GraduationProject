# test fixture

import os
import tempfile

import pytest

from flaskr import create_app
from flaskr.db import get_db, init_db

import socket
import time


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
            '/login/?code={}'.format(code)
        )


    def logout(self):
        return self._client.get('/login/logout')


    def get_img(self):
        return self._client.get('/stream/')


@pytest.fixture
def auth(client):
    return AuthActions(client)


# device actions
class DeviceActions(object):
    ''' management of device login '''

    def __init__(self, client, socket_enabled):
        self._client = client
        self._socket = socket.socket()


    def login(self, device_id='test', device_key='123456'):
        rv = self._client.get(
            '/device/?device_id={}&device_key={}'.format(device_id, device_key)
        )
        assert rv.data == b'OK'

        self._socket = socket.socket()
        self._socket.connect(('127.0.0.1', 6000))

        data = self._socket.recv(1024)
        assert b'established' in data

        return rv


    def logout(self):
        self._socket.close()


    def upload(self, img):
        self._socket.send(img)
        time.sleep(1)


@pytest.fixture
def dev(client, socket_enabled):
    return DeviceActions(client, socket_enabled)
