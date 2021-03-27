import os

from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile('shhrink.cfg', silent=True)
    else:
        app.config.from_mapping(test_config)

    app.config.update(
            DATABASE_PATH = os.path.join(app.instance_path, app.config['DATABASE_FILE']),
            UPLOADS_PATH = os.path.join(app.instance_path, app.config['UPLOADS_DIR'])
            )

    try:
        os.makedirs(app.instance_path)
        os.makedirs(app.config['UPLOADS_PATH'])
    except OSError:
        pass

    from shhrink.shhrink import bp
    app.register_blueprint(bp)

    return app

