import os

from flask import Flask

from app import db
from app.api import bp as api_bp


def create_app(test_config=None):
    app = Flask(__name__)
    if test_config is None:
        env = os.getenv('FLASK_ENV')
        if env == 'production':
            app.config.from_pyfile('settings/prod.py')
        elif env == 'development':
            app.config.from_pyfile('settings/dev.py')
        else:
            raise ValueError('Unknown FLASK_ENV variable')
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)

    app.register_blueprint(api_bp)

    return app
