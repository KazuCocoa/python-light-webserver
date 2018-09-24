import socket

def view(request):
    if request['PATH_INFO'] == '/':
        body = '''
        <html><body>
            <h1>Hello</h1>
        </body></html>
        '''
        resp = ('200 OK', [('Content-Type', 'text/html')], body)
    else:
        resp = '''
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
        s.bind(('127.0.0.1', 8081))
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
