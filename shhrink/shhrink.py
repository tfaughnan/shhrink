import hashlib
import os
import random
import re

from flask import (Blueprint, current_app, make_response, redirect,
                   render_template, request, send_from_directory)
import magic
import werkzeug.exceptions

from shhrink.db_utils import get_db

bp = Blueprint('shhrink', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    urlout = ''
    if request.method == 'POST':
        if 'filein' in request.files and request.files['filein'].filename:
            urlout = handle_file_post(request.files['filein'])
        elif 'urlin' in request.form:
            urlout = handle_url_post(request.form['urlin'])
        else:
            output = (
                    'If you\'re trying to POST with cURL, '
                    'use the appropriate /url or /file endpoint\n'
                    )
            return make_response(output, 405)

    return render_template(
            'index.html',
            urlout=urlout,
            max_file_bytes=current_app.config['MAX_CONTENT_LENGTH']
            )


@bp.route('/url', methods=('GET', 'POST'))
def url_endpoint():
    output = ''
    if request.method == 'POST':
        try:
            assert len(request.form) == 1
        except AssertionError:
            output = (
                    'Try something more like the following:\n'
                    '\tcurl -d "$URL" {shhrink_url}/url\n'
                    'or alternatively:\n'
                    '\tcurl -F "url=$URL" {shhrink_url}/url\n'
                    ).format(shhrink_url=current_app.config['SHHRINK_URL'])
            return make_response(output, 400)

        urlin = next(request.form.values())
        if not urlin:
            urlin = next(request.form.keys())
        urlout = handle_url_post(urlin)
        output = f'{urlout}\n'

    return output


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
    output = ''
    if request.method == 'POST':
        try:
            assert len(request.files) == 1
        except AssertionError:
            output = (
                    'Try something more like the following:\n'
                    '\tcurl -F "f=@$FILE" {shhrink_url}/file\n'
                    ).format(shhrink_url=current_app.config['SHHRINK_URL'])
            return make_response(output, 400)

        filein = next(request.files.values())
        urlout = handle_file_post(filein)
        output = f'{urlout}\n'

    return output


def handle_file_post(filein):
    filename = hash_data(filein.read())
    filepath = os.path.join(current_app.config['UPLOADS_PATH'], filename)
    filein.seek(0)
    filein.save(filepath)

    key = generate_key()
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
        if db.select_by_key(key) or key in current_app.config['RESERVED_KEYS']:
            key = generate_key(attempts=attempts+1)
    else:
        # uhh log something
        pass

    return key


def random_key():
    key = ''
    symbols = current_app.config['KEY_SYMBOLS']

    # Gives us roughly 238k unique keys using a-zA-Z0-9
    # Could allow indefinite number based on current database size,
    # but i'm prob the only person who will use this thing
    N = len(symbols)
    n = random.randrange(0, N**3)

    while n:
        n, r = divmod(n, N)
        key = symbols[r] + key
    return key


def urlout_from_key(key):
    return f'{current_app.config["SHHRINK_URL"]}/{key}'


def hash_data(data):
    return hashlib.md5(data).hexdigest()


def render_file(filename):
    uploads_path = current_app.config['UPLOADS_PATH']
    filepath = os.path.join(uploads_path, filename)
    mimetype = magic.from_file(filepath, mime=True)

    # some browsers (*cough* firefox *cough*) are dumb about rendering
    # plain text files that don't have a .txt extension
    # this also prevents browsers from rendering uploaded html files
    if re.match(r'text/.*', mimetype):
        mimetype = 'text/plain'

    try:
        return send_from_directory(uploads_path, filename, mimetype=mimetype)
    # file was likely deleted on server, so a 410 Gone
    # status code makes more sense than a 404 Not Found
    except werkzeug.exceptions.NotFound:
        raise werkzeug.exceptions.Gone


@bp.route('/fyi/<f>')
def serve_static_page(f):
    directory = os.path.join(
            current_app.root_path,
            current_app.config['STATIC_PAGE_DIR']
            )
    for item in os.listdir(directory):
        if f == os.path.splitext(item)[0]:
            f = item
            break
    try:
        return send_from_directory(directory, f)
    except (werkzeug.exceptions.NotFound):
        return redirect('/')
