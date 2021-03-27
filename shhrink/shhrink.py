import os
import io
import time
import hashlib
from random import randrange

# TODO: reevaluate which imports are actually needed
from flask import current_app, Blueprint, redirect, render_template, request, send_from_directory, make_response
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from shhrink.db_utils import get_db

bp = Blueprint('shhrink', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    urlout=''
    if request.method == 'POST':
        if 'filein' in request.files and request.files['filein'].filename != '':
            urlout = handle_file_post(request.files['filein'])
        elif 'urlin' in request.form:
            urlout = handle_url_post(request.form['urlin'])
        else:
            return 'Nope', 405

    return render_template('index.html', urlout=urlout, max_file_bytes=current_app.config['MAX_FILE_BYTES'])


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

def handle_url_post(urlin):
    urlout = ''
    if urlin:
        db = get_db()
        query = db.select_by_value(urlin)
        if query:
            key = query[2]
        else:
            if not urlin.startswith('http'):
                urlin = f'http://{urlin}'
            key = generate_key()
            db.add_entry(key, urlin, type_='url')
        urlout = urlout_from_key(key)

    return urlout

@bp.route('/file', methods=('GET', 'POST'))
def file_endpoint():
    urlout = ''
    if request.method == 'POST':
        data = list(request.form)[0].encode()

        # TODO: check file size
        
        stream = io.BytesIO(data)
        filename = hash_data(data)
        filein = FileStorage(stream, filename=filename)

        urlout = handle_file_post(filein)

        try:
            pass
        except:
            pass

    return urlout

def handle_file_post(filein):
    key = generate_key()
    display_filename = secure_filename(filein.filename)
    filename = f'{key}_{display_filename}'
    path = os.path.join(current_app.config['UPLOADS_PATH'], filename)
    filein.save(path)

    db = get_db()
    db.add_entry(key, filename, type_='file')
    urlout = urlout_from_key(key)

    return urlout

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
    if attempts < current_app.config['MAX_ATTEMPTS']:
        key = random_key()
        db = get_db()
        if db.select_by_key(key):
            key = generate_key(attempts=attempts+1)
    else:
        # uhh log something
        pass
    return key

def random_key():
    symbols = current_app.config['KEY_SYMBOLS']
    # TODO: don't hardcode 3 below
    key = ''

    # Gives us roughly 238k unique keys using a-zA-Z0-9
    # Could allow indefinite number based on current database size,
    # but i'm prob the only person who will use this thing 
    N = len(symbols)
    n = randrange(0, N**3)

    while n:
        n, r = divmod(n, N)
        key = symbols[r] + key
    return key

def urlout_from_key(key):
    return f'{current_app.config["SHHRINK_URL"]}/{key}'

def hash_data(data):
    return hashlib.md5(data).hexdigest()

def render_file(filename):
    # TODO: MIME detection

    mimetype = 'text/plain'

    return send_from_directory(current_app.config['UPLOADS_PATH'], filename, mimetype=mimetype)

