# run server

from waitress import serve
from flaskr import create_app
from instance import config


app = create_app()
serve(
    app,
    host=config.SERVER_IP,
    port=8080,
    _quiet=True
)
