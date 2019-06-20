import os

TESTING = False

SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('FLASK_SECRET_KEY is not set')

SERVER_NAME = os.getenv('SERVER_NAME')