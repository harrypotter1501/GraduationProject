# factory for app init

import os
from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        ROOT_FOLDER = os.path.dirname(os.path.abspath('__file__')),
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
        APP_ID = 'wxc81559edfce187c9',
        APP_SECRET = '65261bd974da4ce92c0dd24dd29c575f',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register functions
    from . import db
    db.init_app(app)

    from . import login
    app.register_blueprint(login.bp)

    from . import stream
    app.register_blueprint(stream.bp)

    from . import device
    app.register_blueprint(device.bp)

    # generate websocket server instance
    from .socket_server import init_server
    init_server()

    # test url
    @app.route('/test')
    def test():
        return 'TEST'

    return app
