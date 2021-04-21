# stream blueprint & view

from flask import (
    Blueprint, g, request, session, make_response
)
from .db import get_db
from .login import login_required
from .socket_server import pop_img


# blueprint
bp = Blueprint('stream', __name__, url_prefix='/stream')


# stream
@bp.route('/')
@login_required
def stream():
    ''' return latest image obtained from socket '''

    device_id = g.user['devices']
    if device_id is None:
        return 'Server error'

    img = pop_img(device_id)

    from io import BytesIO
    arr = BytesIO()
    img.save(arr, format='JPEG')
    res = make_response(arr.getvalue())
    res.headers['Content-Type'] = 'image/jpeg'

    return res


@bp.route('/test')
@login_required
def test():
    ''' this is a test url with login '''

    return 'test'
