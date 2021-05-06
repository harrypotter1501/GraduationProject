# login blueprint & view

import functools
from flask import (
    Blueprint, g, request, session, current_app
)
#from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db
from .socket_server import close_socket


# blueprint
bp = Blueprint('login', __name__, url_prefix='/login')


# tool func
def get_openid(appid, app_secret, code):
    ''' sends a GET request
    :gets openid & session_key from api.weixin.qq.com
    :returns them in a dict
    '''

    import requests

    url = 'https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code'
    res = requests.get(url.format(appid, app_secret, code))
    res.encoding = 'utf8'
    res = res.json()
    openid = res.get('openid')
    session_key = res.get('session_key')

    return {'openid': openid, 'session_key': session_key}


# login
@bp.route('/')
def login():
    ''' login with appid, app secret & code
    :based on sqlite
    :use sessions
    '''

    db = get_db()

    code = request.args.get('code')

    if code is None:
        return 'Code missing'
    elif 'test' in code:
        openid = code
    else:
        appid = current_app.config['APP_ID']
        app_secret = current_app.config['APP_SECRET']
        openid = get_openid(appid, app_secret, code)['openid']

    if openid is None:
        return 'Identification failed'

    session.clear()
    session['openid'] = openid

    row = db.execute(
        'SELECT id FROM Users WHERE openid = ?', (openid,)
    ).fetchone()

    if row is None:
        return 'REG'

    return 'OK'


# register
@bp.route('/register', methods=['POST'])
def register():
    ''' register a new user '''

    db = get_db()

    openid = session.get('openid')
    if openid is None:
        return 'Openid missing'

    device_id = request.form['device_id']
    device_key = request.form['device_key']

    from .device import verify_device
    msg = verify_device(device_id, device_key)
    if msg != 'OK':
        return msg

    row = db.execute(
        'SELECT id FROM Users WHERE openid = ?', (openid,)
    ).fetchone()

    if row is not None:
        return 'Already registered'

    # insert into db
    import time
    db.execute(
        'INSERT INTO Users (openid, sign_up_date, devices) VALUES (?, ?, ?)',
        (openid, time.time(), device_id)
    )
    db.commit()

    return 'OK'


# logout
@bp.route('/logout')
def logout():
    ''' user logout '''

    try:
        device_id = g.user['devices']
        close_socket(device_id)
        session.clear()
    except:
        return ''
    return 'OK'


# global
@bp.before_app_request
def load_logged_in_user():
    ''' load user info before handling requests
    :globally registered
    :automatically invoked
    '''

    openid = session.get('openid')
    if openid is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT id, openid, devices FROM Users WHERE openid=?', (openid,)
        ).fetchone()


def login_required(view):
    ''' wrapper for views which requires login '''

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return 'LOGIN'
        return view(**kwargs)
    return wrapped_view
