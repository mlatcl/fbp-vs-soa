import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        # create database connection if it does not exist
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # set return of rows that behave like dicts
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        # close database connection if it exists
        db.close()


def init_db():
    db = get_db()
    # execute SQL commands in the schema.sql file
    with current_app.open_resource('./data/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    # clear the existing data and create new tables
    init_db()
    click.echo('Initialized the database.')


# register functions with the app
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

