import os

TESTING = False

SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('FLASK_SECRET_KEY is not set')

SERVER_NAME = os.getenv('SERVER_NAME')

POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
if not POSTGRES_PASSWORD:
    raise ValueError('POSTGRES_PASSWORD is not set')

POSTGRES_PORT = os.getenv('POSTGRES_PORT')
if not POSTGRES_PORT:
    raise ValueError('POSTGRES_PORT is not set')

POSTGRES_USER = os.getenv('POSTGRES_USER')
if not POSTGRES_USER:
    raise ValueError('POSTGRES_USER is not set')

POSTGRES_DB = os.getenv('POSTGRES_DB')
if not POSTGRES_DB:
    raise ValueError('POSTGRES_DB is not set')