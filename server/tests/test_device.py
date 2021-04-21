# test device

import pytest
from flaskr.socket_server import SocketServer, get_thread, pop_img


def test_create_close_socket(client, dev):
    assert client.get('/device/').status_code == 200

    assert b'OK' in dev.login().data
    threads = SocketServer.instance().threads
    assert len(threads) > 0

    dev.logout()
    import time
    time.sleep(1)
    assert len(threads) == 0


def test_reconnect(client, dev):
    assert b'OK' in dev.login().data
    assert b'OK' in dev.login().data
    # assert b'OK' in dev.login().data

    dev.logout()


def test_uplaod(client, dev):
    dev.login()

    with open('tests/demo.jpg', 'rb') as f:
        dev.upload(f.read())

    t = get_thread('test')
    assert t is not None
    q = get_thread('test').buffer.images
    assert q.qsize() > 0

    dev.logout()

    img = pop_img('test')
    assert img is not None
