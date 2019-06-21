import os

TESTING = False

SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('FLASK_SECRET_KEY is not set')

SERVER_NAME = os.getenv('SERVER_NAME')

POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_DB = os.getenv('POSTGRES_DB')