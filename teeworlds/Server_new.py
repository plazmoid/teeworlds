import socketserver
import threading
import time

CLIENTS = []

class TWServerHandler(socketserver.BaseRequestHandler):

    def __init__(self, *args):
        CLIENTS.append(self)
        super().__init__(*args)

    def handle(self):
        while 1:
            self.data = self.request.recv(1024)
            for client in CLIENTS:
                if client != self:
                    client.request.send(self.data)
            time.sleep(0.001)
    
    
class TWServer(socketserver.ThreadingTCPServer):
    pass


server = TWServer(('', 31337), TWServerHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()