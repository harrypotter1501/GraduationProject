# stream blueprint & view

from flask import (
    Blueprint, g, request, session, make_response
)
from .db import get_db
from .login import login_required
from .device import device_required
from .socket_server import pop_img, pop_sensors, send_command


# blueprint
bp = Blueprint('stream', __name__, url_prefix='/stream')


# stream
@bp.route('/')
@login_required
@device_required
def stream():
    ''' return latest image obtained from socket '''

    device_id = g.user['devices']
    if device_id is None:
        return 'Server error'

    img = pop_img(device_id)
    if img is None:
        from PIL import Image
        img = Image.open('flaskr/demo.jpg')

    from io import BytesIO
    arr = BytesIO()
    img.save(arr, format('PNG'))

    res = make_response(arr.getvalue())
    res.headers['Content-Type'] = 'image/jpeg'

    return res


# sensors
@login_required
@device_required
@bp.route('/sensors')
def sensors():
    ''' return sensor data from socket '''

    device_id = g.user['devices']
    if device_id is None:
        return 'Server error'

    data = pop_sensors(device_id)

    return {
        'temperature': data.temperature,
        'humidity': data.humidity,
        'time': data.time
    }


@login_required
@device_required
@bp.route('/command', methods=['POST'])
def command():
    ''' upload commands to server
    :format - {
    :    "DHT": [True, False],
    :    "CAM": [True, False],
    :    "MODE": ["QVGA", "VGA", "SVGA", "XGA"],
    :    "FRAME": ["LOW", "MEDIUM", "HIGH"]
    :}
    '''

    dht = request.form['DHT']
    cam = request.form['CAM']
    mode = request.form['MODE']
    frame = request.form['FRAME']

    dht_n = 1 if dht else 0
    cam_n = 1 if cam else 0
    mode_n = ["QVGA", "VGA", "SVGA", "XGA"].index(mode)
    frame_n = ["LOW", "MEDIUM", "HIGH"].index(frame)

    cmd = (dht_n) + (cam_n<<1) + (mode_n<<2) + (frame_n<<4)

    device_id = g.user['devices']
    res = send_command(device_id, cmd)

    print(
        '''Command Sent:
        From: {} - To: {}
        {}'''.format(g.user['openid'], device_id, hex(cmd))
    )

    if res is None:
        return 'No alive socket'
    return res


@bp.route('/alive')
@login_required
@device_required
def alive():
    ''' this is a test url with login & device '''

    return 'OK'
