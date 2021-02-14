import os

from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY = 'dev',
            DATABASE = os.path.join(app.instance_path, 'shhrink.db'),
            )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

#    @app.route('/hello')
#    def hello():
#        return 'Hello, World!'

    from shhrink import shhrink
    app.register_blueprint(shhrink.bp)

#    from shhrink.db import ShhrinkDb
#    db = ShhrinkDb('shhrink.db')

    return app

