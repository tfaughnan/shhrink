import functools
from random import randrange

# TODO: reevaluate which imports are actually needed
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from shhrink.db_utils import get_db

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
            print('we good homie')
            print(f'INPUT: {urlin}')
            urlout = shorten_url(urlin)
            print(f'OUTPUT: {urlout}')

            db = get_db()
            db.add_entry(urlin, urlout)
        else:
            print('nah fam that aint it')
            flash(error)

    return render_template('index.html', urlout=urlout)

def shorten_url(url):
    BASE = 'https://shhr.ink/'
    key = str(randrange(0, 1000)).zfill(3)
    return BASE + key

