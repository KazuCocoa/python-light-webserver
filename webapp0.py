import socket

def view(request):
    if request['PATH_INFO'] == '/':
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
        resp = ('200 OK', [('Content-Type', 'text/html')], body)
    elif request['PATH_INFO'] == '/static/style.css':
        headers = [
            ('Content-Type', 'text/css'),
        ]
        resp = ('200 OK', headers, open('static/style.css', 'rb').read())
    elif request['PATH_INFO'] == '/static/image.jpeg':
        headers = [
            ('Content-Type', 'image/jpg'),
        ]
        resp = ('200 OK', headers, open('static/image.jpg', 'rb').read())
    else:
        body = '''
        NO PAGE
        '''
        resp = ('404 NOT FOUND', [('Content-Type', 'text/plain')], body)
    return resp

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
    status, headers, body = view(request)
    if isinstance(body, str):
        body = body.encode('utf=8')
    raw_response = create_response(status, headers, body)
    return raw_response

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
