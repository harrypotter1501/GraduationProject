# test device

import pytest
from flaskr.socket_server import SocketServer, close_socket

import time


def test_no_device(client, auth, dev):
    rv = client.get('/stream/alive')
    assert rv.status_code == 200
    assert b'LOGIN' in rv.data

    auth.login()
    rv = auth._client.get('/stream/alive')
    assert rv.status_code == 200
    assert b'DEVICE' in rv.data

    dev.login()
    assert b'OK' in client.get('/stream/alive').data
    dev.logout()


def test_create_close_socket(client, dev):
    assert client.get('/device/').status_code == 200

    assert b'OK' in dev.login().data
    assert len(SocketServer.instance().threads) > 0

    # do sth
    time.sleep(1)

    dev.logout()
    assert close_socket('test') == 'OK'
    assert len(SocketServer.instance().threads) == 0


def test_reconnect(client, dev):
    assert b'OK' in dev.login().data
    assert len(SocketServer.instance().threads) == 1

    # do sth
    time.sleep(1)
    
    assert b'OK' in dev.login().data
    assert len(SocketServer.instance().threads) == 1
    # assert b'OK' in dev.login().data

    # do sth
    time.sleep(1)

    dev.logout()
    assert close_socket('test') == 'OK'
    assert len(SocketServer.instance().threads) == 0


