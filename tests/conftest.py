import os

import pytest

from app import create_app
from app.db import init_db


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'POSTGRES_PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'POSTGRES_PORT': os.getenv('POSTGRES_PORT'),
        'POSTGRES_USER': os.getenv('POSTGRES_USER'),
        'POSTGRES_DB': os.getenv('POSTGRES_DB'),
    })

    with app.app_context():
        init_db()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()