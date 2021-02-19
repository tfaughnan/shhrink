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

# TODO: is GET really necessary?
@bp.route('/', methods=('GET', 'POST'))
def index():
    urlout=''
    if request.method == 'POST':
        urlin = request.form['urlin']
        error = None

        # TODO: neaten this mess up!        
        if not urlin:
            error = 'enter a url'
        else:
            db = get_db()
            query = db.select_by_urlin(urlin)
            if query:
                urlout = query[3]
            else:
                urlout = generate_urlout(urlin)
                if urlout is None:
                    error = 'unable to generate valid key'

                if error is None:
                    db.add_entry(urlin, urlout)
        if error:
            flash(error)

    return render_template('index.html', urlout=urlout)

@bp.route('/<key>')
def redirection(key):
    urlout = f'{BASE_URL}/{key}'
    db = get_db()
    query = db.select_by_urlout(urlout)
    if query:
        urlin = query[2]
        r = redirect(urlin)
        db.increment_clicks(urlout)
    else:
        r = redirect('/')
    return r

def generate_urlout(urlin, attempts=0):
    if attempts < MAX_ATTEMPTS:
        key = generate_key(urlin)
        urlout = f'{BASE_URL}/{key}'
        db = get_db()
        if db.select_by_urlout(urlout):
            urlout = generate_urlout(urlin, attempts=attempts+1)
    else:
        urlout = None
    return urlout

def generate_key(urlin):
    # TODO: don't hardcode 3 below
    key = ''
    N = len(SYMBOLS)
    n = randrange(0, N**3)
    while n:
        n, r = divmod(n, N)
        key = SYMBOLS[r] + key
    return key

