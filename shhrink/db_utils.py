import sqlite3
import time

from flask import current_app

def get_db():
    db = ShhrinkDb(current_app.config['DATABASE'])
    print(db.path)
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
                    urlin   TEXT NOT NULL UNIQUE,
                    urlout  TEXT NOT NULL UNIQUE,
                    clicks  INTEGER NOT NULL DEFAULT 0
                )
                ''')

    def add_entry(self, urlin, urlout):
        values = (int(time.time()), urlin, urlout)
        with self.conn:
            c = self.conn.cursor()
            c.execute(
                'INSERT INTO shhrink (time, urlin, urlout) VALUES (?, ?, ?)',
                values)

    def select_by_urlin(self, urlin):
        c = self.conn.cursor()
        c.execute(
            'SELECT * FROM shhrink WHERE urlin=?',
            (urlin,))
        return c.fetchone()
        
    def select_by_urlout(self, urlout):
        c = self.conn.cursor()
        c.execute(
            'SELECT * FROM shhrink WHERE urlout=?',
            (urlout,))
        return c.fetchone()
 
    def increment_clicks(self, urlout):
        pass

