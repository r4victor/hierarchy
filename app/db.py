import time

import psycopg2.extras
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db_conn():
    if 'db_conn' not in g:
        tries = 5
        while tries > 0:
            try:
                g.db_conn = psycopg2.connect(
                    dbname=current_app.config['POSTGRES_DB'],
                    user=current_app.config['POSTGRES_USER'],
                    password=current_app.config['POSTGRES_PASSWORD'],
                    host='postgres',
                    port=current_app.config['POSTGRES_PORT'],
                    cursor_factory=psycopg2.extras.DictCursor,
                )
            except psycopg2.OperationalError:
                time.sleep(1)
                tries -= 1
            else:
                break
        else:
            raise RuntimeError('Could not connect to postgres')

    return g.db_conn


def teardown_db(e=None):
    db_conn = g.pop('db_conn', None)

    if db_conn is not None:
        db_conn.close()


def init_db():
    db_conn = get_db_conn()

    with db_conn.cursor() as cur:
        with current_app.open_resource('schema.sql') as f:
            cur.execute(f.read())
        cur.execute("INSERT INTO node (name, lft, rgt) VALUES ('root', 0, 1)")
    
    db_conn.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()


def init_app(app):
    app.teardown_appcontext(teardown_db)
    app.cli.add_command(init_db_command)
