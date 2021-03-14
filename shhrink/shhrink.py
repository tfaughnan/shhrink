import functools
from random import randrange

# TODO: reevaluate which imports are actually needed
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from shhrink.db_utils import get_db

# TODO: these should be set by config, loaded in __init__.py
BASE_URL = 'https://shhr.ink'
MAX_ATTEMPTS = 10
SYMBOLS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

bp = Blueprint('shhrink', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    urlout=''
    if request.method == 'POST':
        urlout = handle_url_post(request.form['urlin'])

    return render_template('index.html', urlout=urlout)
        
def handle_url_post(urlin):
    urlout = ''
    if urlin:
        db = get_db()
        query = db.select_by_value(urlin)
        if query:
            key = query[2]
        else:
            key = generate_key(urlin)
            if key:
                db.add_entry(key, urlin)
        urlout = urlout_from_key(key)

    return urlout

@bp.route('/url', methods=('GET', 'POST'))
def url_endpoint():
    urlout = ''
    if request.method == 'POST':
        try:
            urlin = list(request.form)[0]
            urlout = handle_url_post(urlin)
        except IndexError as e:
            pass

    return urlout

@bp.route('/<key>')
def redirection(key):
    urlout = urlout_from_key(key)
    db = get_db()
    query = db.select_by_key(key)
    if query:
        urlin = query[3]
        redir = redirect(urlin)
        db.increment_clicks(key)
    else:
        redir = redirect('/')
    return redir

def generate_key(urlin, attempts=0):
    if attempts < MAX_ATTEMPTS:
        key = generate_key(urlin)
        db = get_db()
        if db.select_by_key(key):
            key = generate_key(urlin, attempts=attempts+1)
    else:
        key = None
    return key

def generate_key(urlin):
    # TODO: don't hardcode 3 below
    key = ''
    N = len(SYMBOLS)
    n = randrange(0, N**3)
    while n:
        n, r = divmod(n, N)
        key = SYMBOLS[r] + key
    return key

def urlout_from_key(key):
    return f'{BASE_URL}/{key}'

