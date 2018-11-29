from bottle import request, template, static_file, redirect, Bottle, Jinja2Template, jinja2_view, response
from urllib.parse import unquote
import base64
import re
import unicodedata
import baseconvert

table = {'0': unicodedata.lookup('FACE WITH TEARS OF JOY'),
         '1': unicodedata.lookup('HUNDRED POINTS SYMBOL'),
         '2': unicodedata.lookup('FIRE'),
         '3': unicodedata.lookup('OK HAND SIGN')}

inv_table = {v:k for k,v in table.items()}

app = Bottle()

@app.route('/')
def root():
    return static_file('index.html', '/opt/wsgi/lengthened/static')

@app.route('/get')
def new_link():
    to = request.query.u

    chars = [ord(i) for i in to]
    chars = [baseconvert.base(i, 10, 4, string=True).rjust(4, '0') for i in chars]
    chars = [''.join(map(table.get, i)) for i in chars]
    token = ''.join(chars)
    url = f'http://lengthened.link/emoji?u={token}'
    return f"<!doctype html><html><head></head><body><a href='{url}'>{url}</a></body></html>"

@app.route('/emoji')
def emoji():
    token = request.query.u
    nums = ''.join(map(inv_table.get, token))
    chunks = re.findall('....', nums) # splits into 4-char chunks
    chunks = [int(baseconvert.base(c, 4, 10, string=True)) for c in chunks]
    url = ''.join(chr(i) for i in chunks)

    response.set_header('Location', url)
    response.status = 302
    return response

@app.route('/<name:re:.+\..+>')
def get(name):
    name = request.url.split('lengthened.link/', 1)[1]
    proto = 'http'
    res = re.split('(https?)(?::|\/|\%3A|\%2F)+', name, 1)
    if len(res) == 1:
        name = res[0]
    else:
        _, proto, name = res

    response.set_header('Location', proto + '://' + name)
    response.status = 302
    return response


app.catchall = False # report errors to uWSGI
