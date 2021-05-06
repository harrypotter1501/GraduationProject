# device

import functools

from flask import (
    Blueprint, g, request, session
)

from .db import get_db
from .login import login_required
from .socket_server import create_socket, socket_alive


# blueprint
bp = Blueprint('device', __name__, url_prefix='/device')


# tool func
def verify_device(device_id, device_key):
    ''' check device validity
    :return message
    '''

    db = get_db()

    row = db.execute(
        'SELECT * FROM Devices WHERE device_id = ?', (device_id,)
    ).fetchone()

    if row is None:
        return 'No such device as: {}'.format(device_id)
    elif row['device_key'] != device_key:
        return 'Wrong device-key'
    else:
        return 'OK'


# connect
@bp.route('/')
def device():
    ''' create server socket
    :accept a request from device
    :create a new socket thread on server & wait connection
    '''

    device_id = request.args.get('device_id')
    device_key = request.args.get('device_key')

    if device_id is None or device_key is None:
        return 'Invalid request'

    msg = verify_device(device_id, device_key)
    if msg != 'OK':
        return msg

    #create socket
    device_ip = request.remote_addr
    create_socket(device_id, device_ip)

    return 'OK'


def device_required(view):
    ''' wrapper for views which requires a device
    :should be used with and after login_required
    '''

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        device_id = g.user['devices']
        if not socket_alive(device_id):
            return 'DEVICE'
        return view(**kwargs)
    return wrapped_view
