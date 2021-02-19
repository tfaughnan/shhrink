import os
import tempfile

import pytest

from shhrink import create_app
from shhrink.db_utils import get_db

with open(os.path.join(os.path.dirname(__file__), 'test.sql'), 'r') as f:
    sql = f.read()

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path
        })
    
    db = get_db()
    db.executescript(sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

