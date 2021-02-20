import os
import sqlite3

import pytest

from shhrink.db_utils import get_db

def test_get_db(app):
    with app.app_context():
        db = get_db()
        assert os.path.exists(db.path)

