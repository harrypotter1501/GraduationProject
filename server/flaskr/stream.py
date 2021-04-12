# stream blueprint & view

from flask import (
    Blueprint, g, request, session, Response
)
from .db import get_db
from .login import login_required
from .socket_server import get_socket_buffer


# blueprint
bp = Blueprint('stream', __name__, url_prefix='/stream')


# stream
@bp.route('/')
@login_required
def stream():
    ''' return latest image obtained from socket '''

    db = get_db()

    return 'pass'
