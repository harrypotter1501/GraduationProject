# test stream

import pytest

from flaskr.socket_server import get_thread, pop_img, close_socket, send_command


def test_upload(client, dev):
    dev.login()

    with open('tests/demo.jpg', 'rb') as f:
        dev.upload(f.read())

    t = get_thread('test')
    assert t is not None

    q = t.buffer.images
    assert q.qsize() > 0

    img = pop_img('test')
    assert img is not None

    dev.logout()
    close_socket('test')


def test_command(client, auth, dev):
    dev.login()
    auth.login()

    assert auth.command(dht=True, cam=True).status_code == 200
    res =  dev.recv()
    dev.logout()
    close_socket('test')

    assert int.from_bytes(res, 'little') == 0b00010011


def test_match(client, auth, dev):
    auth.login('test_system')
    dev.login('test_sys', 'abcdef')

    with open('tests/demo.jpg', 'rb') as f:
        dev.upload(f.read())
    res = auth.get_img()
    assert res.status_code == 200
    dev.logout()
    auth.logout()

    img = res.data
    assert img is not None


# def test_match_multiple(client, auth, dev):
#     pass


def test_sensors(client, auth, dev):
    dev.login()
    dev.sensors()

    auth.login()
    rv = auth.get_sensors()

    dev.logout()
    auth.logout()

    assert b'25' in rv.data
