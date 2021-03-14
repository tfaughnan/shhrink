import os
import functools
from random import randrange

# TODO: reevaluate which imports are actually needed
from flask import Blueprint, flash, redirect, render_template, request, session, url_for, send_from_directory, make_response
from werkzeug.utils import secure_filename

from shhrink.db_utils import get_db

# TODO: these should be set by config, loaded in __init__.py
BASE_URL = 'https://shhr.ink'
# TODO: mkdir for below if needed
UPLOAD_FOLDER = '/tmp/shhrink-uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_BYTES = 10_000_000
MAX_ATTEMPTS = 10
SYMBOLS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

bp = Blueprint('shhrink', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    urlout=''
    if request.method == 'POST':
        if 'filein' in request.files and request.files['filein'].filename != '':
            urlout = handle_file_post(request.files['filein'])
        else: 
            urlout = handle_url_post(request.form['urlin'])

    return render_template('index.html', urlout=urlout, max_file_bytes=MAX_FILE_BYTES)
        
def handle_url_post(urlin):
    urlout = ''
    if urlin:
        db = get_db()
        query = db.select_by_value(urlin)
        if query:
            key = query[2]
        else:
            key = generate_key()
            if key:
                db.add_entry(key, urlin, type_='url')
        urlout = urlout_from_key(key)

    return urlout

def handle_file_post(filein):
    key = generate_key()
    display_filename = secure_filename(filein.filename)
    filename = f'{key}_{display_filename}'
    path = os.path.join(UPLOAD_FOLDER, filename)
    filein.save(path)

    db = get_db()
    db.add_entry(key, filename, type_='file')
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

@bp.route('/file', methods=('GET', 'POST'))
def file_endpoint():
    return ''

@bp.route('/<key>')
def keydirect(key):
    db = get_db()
    query = db.select_by_key(key)
    if query:
        type_ = query[4]
        if type_ == 'url':
            urlin = query[3]
            content = redirect(urlin)
        elif type_ == 'file':
            filename = query[3]
            content = render_file(filename)
        db.increment_clicks(key)
    else:
        content = redirect('/')
    return content

def generate_key(attempts=0):
    if attempts < MAX_ATTEMPTS:
        key = random_key()
        db = get_db()
        if db.select_by_key(key):
            key = generate_key(attempts=attempts+1)
    else:
        key = None
    return key

def random_key():
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

def render_file(filename):

    mimetype = 'text/plain'


    return send_from_directory(UPLOAD_FOLDER, filename, mimetype=mimetype)
    



