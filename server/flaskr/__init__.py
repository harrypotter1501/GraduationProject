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
        SERVER_IP = '127.0.0.1',
        SOCKET_PORT = 6000,
        BUFSIZE_K = 500,
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
    ip = app.config['SERVER_IP']
    port = app.config['SOCKET_PORT']
    bufsize_k = app.config['BUFSIZE_K']
    init_server(ip, port)
    print(' * Socket Server Running on {}:{}'.format(ip, port))

    # test url
    @app.route('/test')
    def test():
        return 'This is a test url'

    print(' * Server Started on {}:{}'.format(ip, 8080))

    return app
