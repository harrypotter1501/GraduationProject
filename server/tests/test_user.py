# test device

import pytest
from flask import g, session
from flaskr.db import get_db


def test_login(client, auth):
    assert client.get('/login/').status_code == 200
    auth.login()

    with client:
        client.get('/stream/')
        assert session['openid'] == 'test'
        assert g.user is not None
        assert g.socket is not None


def test_register(client, auth, app):
    assert auth.login('test1')
    # with client:
    #     assert client.post(
    #         '/login/register',
    #         data={'device_id': 'test', 'device_key': '123456'}
    #     ).data.decode() == 'OK'

    #     with app.app_context():
    #         assert get_db().execute(
    #             "SELECT * FROM Users WHERE openid = 'test'"
    #         ).fetchone() is not None


def test_socket(client, dev):
    assert client.get('/device/').status_code == 200
    assert dev.login().status_code == 200
