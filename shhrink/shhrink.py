import functools
from random import randrange

# TODO: reevaluate which imports are actually needed
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from shhrink.db_utils import get_db

BASE_URL = 'https://shhr.ink'
bp = Blueprint('shhrink', __name__)

# TODO: is GET really necessary?
@bp.route('/', methods=('GET', 'POST'))
def index():
    urlout=''
    if request.method == 'POST':
        urlin = request.form['urlin']
        error = None
        
        if not urlin:
            error = 'enter a url'
        # TODO: also check if url is *valid*, e.g. by pinging it or something idk
        elif False:
            error = 'invalid url'

        if error is None:
            # TODO: do the shortening and add to database
            db = get_db()

            query = db.select_by_urlin(urlin)
            if query:
                urlout = query[3]
            else:
                urlout = generate_urlout(urlin)
                db.add_entry(urlin, urlout)

            print('we good homie')
            print(f'INPUT: {urlin}')
            print(f'OUTPUT: {urlout}')

        else:
            print('nah fam that aint it')
            flash(error)

    return render_template('index.html', urlout=urlout)

@bp.route('/<key>')
def redirection(key):
    urlout = f'{BASE_URL}/{key}'
    print(f'{urlout=}')
    db = get_db()
    query = db.select_by_urlout(urlout)
    print(f'{query=}')
    if query:
        urlin = query[2]
        r = redirect(urlin)
    else:
        r = redirect('/')
    return r

def generate_urlout(urlin):
    key = generate_key(urlin)
    urlout = f'{BASE_URL}/{key}'
    return urlout

def generate_key(urlin):
    key = str(randrange(0, 1000)).zfill(3)
    return key

