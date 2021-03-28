import sqlite3
import time

from flask import current_app


def get_db(path=None):
    if path is None:
        db = ShhrinkDb(current_app.config['DATABASE_PATH'])
    else:
        db = ShhrinkDb(path)
    return db


class ShhrinkDb:
    def __init__(self, path=None):
        self.path = path
        self.conn = sqlite3.connect(path)

        with self.conn:
            c = self.conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS shhrink (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    time    INTEGER NOT NULL,
                    key     TEXT NOT NULL UNIQUE,
                    value   TEXT NOT NULL,
                    type    TEXT NOT NULL,
                    clicks  INTEGER NOT NULL DEFAULT 0
                )
                ''')

    def add_entry(self, key, value, type_='url'):
        values = (int(time.time()), key, value, type_)
        with self.conn:
            c = self.conn.cursor()
            c.execute(
                'INSERT INTO shhrink (time, key, value, type) VALUES (?, ?, ?, ?)',
                values)

    def select_by_value(self, value):
        c = self.conn.cursor()
        c.execute(
            'SELECT * FROM shhrink WHERE value=?',
            (value,))
        return c.fetchone()

    def select_by_key(self, key):
        c = self.conn.cursor()
        c.execute(
            'SELECT * FROM shhrink WHERE key=?',
            (key,))
        return c.fetchone()

    def increment_clicks(self, key):
        query = self.select_by_key(key)
        id_ = query[0]
        clicks = query[5]

        with self.conn:
            c = self.conn.cursor()
            c.execute(
                'UPDATE shhrink SET clicks=? WHERE id=?',
                (clicks + 1, id_))

    def executescript(self, sql):
        with self.conn:
            c = self.conn.cursor()
            c.executescript(sql)
