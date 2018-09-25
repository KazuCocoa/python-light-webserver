import os
from mimetypes import guess_type
import socket

def index_view(request):
    body = '''
    <html>
    <head>
        <link href="/static/style.css" rel="stylesheet">
    </head>
    <body>
        <h1>Hello World!</h1>
        <img src="/static/image.jpg">
    </body>
    </html>
    '''
    return ('200 OK', [('Content-Type', 'text/html')], body)

def file_view(request):
    path = request['PATH_INFO']
    path = path.lstrip('/')
    if not os.path.isfile(path):
        return notfound_view(request)

    ct, _ = guess_type(path)
    if ct is None:
        ct = 'application/octet-stream'
    headers = [
        ('Content-Type', ct),
    ]
    return ('200 OK', headers, open(path, 'rb').read())

def notfound_view(reqeust):
    return ('404 NOT FOUND', [('Content-Type', 'text/plain')], 'NO PAGE')

patterns = {
    '/static/': file_view,
    '/': index_view,
}

def dispatch(request):
    path_info = request['PATH_INFO']
    for path, view in patterns.items():
        if path_info.startswith(path):
            return view
    return notfound_view

def create_request(raw_request):
    if isinstance(raw_request, bytes):
        raw_request = raw_request.decode('utf-8')
    print(raw_request)
    header, body = raw_request.split('\r\n\r\n', 1)
    headers = header.splitlines()
    method, path, proto = headers[0].split(' ', 2)
    reqeust = {
        'headers': headers[1:],
        'body': body,
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'SERVER_PROTOCOL': proto,
    }
    return reqeust

def create_response(status, headers, body):
    status_line = ('HTTP/1.1 ' + status).encode('utf-8')
    hl = []
    for k, v in headers:
        h = '%s: %s' % (k, v)
        hl.append(h)
    header = ('\r\n'.join(hl)).encode('utf-8')
    if isinstance(body, str):
        body = body.encode('utf-8')
    raw_response = status_line + b'\r\n' + header + b'\r\n\r\n' + body
    print(raw_response)
    return raw_response

def app(raw_request):
    request = create_request(raw_request)
    view  = dispatch(request)
    status, headers, body = view(request)
    if isinstance(body, str):
        body = body.encode('utf=8')
    raw_response = create_response(status, headers, body)
    return raw_response

def wsgiapp(environ, start_response):
    request = environ
    view = dispatch(request)
    status, headers, body = view(request)
    if isinstance(body, str):
        body = body.encode('utf-8')
    start_response(status, headers)
    return [body]

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 8082))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                raw_request = b''
                while True:
                    chunk = conn.recv(4096)
                    raw_request += chunk
                    if len(chunk) < 4096:
                        break
                raw_response = app(raw_request)
                conn.sendall(raw_response)

if __name__ == '__main__':
    main()
