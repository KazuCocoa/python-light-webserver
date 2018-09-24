import socket

def view(raw_request):
    print(raw_request)
    return 'HTTP/1.1 501\r\n\r\nSorry\n'

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 8000))
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
