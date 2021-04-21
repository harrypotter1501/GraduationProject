# test stream

import pytest

from flaskr.socket_server import pop_img


def test_match(client, auth, dev):
    auth.login()
    dev.login()

    with open('tests/demo.jpg', 'rb') as f:
        dev.upload(f.read())
    res = auth.get_img()
    assert res.status_code == 200
    dev.logout()

    img = res.data
    assert img is not None
