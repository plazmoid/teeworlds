import socket as s
import socketserver
import threading
import msvcrt

class TWClientHandler(socketserver.BaseRequestHandler):
    
    def handle(self):
        print(self.request.recv(1024).decode('ascii'))
              

class TWClient(socketserver.BaseServer):

    def __init__(self, socket, RequestHandlerClass):
        super().__init__(socket.getsockname(), RequestHandlerClass)
        self.socket = socket
        self.server_address = self.socket.getsockname()

    def server_close(self):
        self.socket.close()

    def fileno(self):
        return self.socket.fileno()

    def get_request(self):
        return self.socket.accept()

    def shutdown_request(self, request):
        try:
            request.shutdown(s.SHUT_WR)
        except OSError:
            pass
        self.close_request(request)

    def close_request(self, request):
        request.close()

with s.socket(s.AF_INET, s.SOCK_STREAM, s.IPPROTO_TCP) as sock:
    sock.connect(('127.0.0.1', 31337))
    client = TWClient(sock, TWClientHandler)
    client_thread = threading.Thread(target=client.serve_forever)
    client_thread.start()
    while True:
        if msvcrt.kbhit():
            sock.send(msvcrt.getch()) 