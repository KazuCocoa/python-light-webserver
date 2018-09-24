import socket
import textwrap

def view(raw_request):
    header, body = raw_request.split('\r\n\r\n', 1)
    print(header)
    print(body)
    headers = header.splitlines()
    method, path, version = headers[0].split(' ', 2)

    if path == '/':
        resp = textwrap.dedent('''\
        HTTP/1.1 200 OK

        <html><body>
            <h1>Hello</h1>
        </body></html>
        ''')
    else:
        resp = textwrap.dedent('''\
        HTTP/1.1 404 NOT FOUND

        NO PAGE
        ''')

    return resp

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
                raw_response = view(raw_request.decode('utf-8'))
                conn.sendall(raw_response.encode('utf-8'))

if __name__ == '__main__':
    main()
