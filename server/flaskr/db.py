# database

import click
import sqlite3
from flask import g, current_app
from flask.cli import with_appcontext


def get_db():
    ''' get a database instance
    :returns a db instance from g
    :creates one if not exists
    '''

    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    ''' close db connection and remove instance from g '''

    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    ''' initialize database
    :creates tables (Devices, Users, Logs)
    :drop old ones if exists
    '''

    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    ''' clear existing db data and create new tables '''

    init_db()
    click.echo('Database initialized.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
