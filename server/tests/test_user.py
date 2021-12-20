# test user

import pytest
from flask import g, session
from flaskr.db import get_db


def test_login_logout(client, auth):
    assert client.get('/login/').status_code == 200
    auth.login()

    with client:
        client.get('/stream/test/')
        assert session['openid'] == 'test'
        assert g.user is not None

    with client:
        rv = auth.logout()
        assert rv.data == b'OK'
        assert 'openid' not in session


def test_register(client, auth, app):
    assert auth.login('test1').data == b'REG'

    res =  client.post(
        '/login/register',
        data={'device_id': 'test', 'device_key': '123456'}
    )
    assert res.data == b'OK'

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM Users WHERE openid = 'test'"
        ).fetchone() is not None
