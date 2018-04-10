import struct
import time

import socket as s

#TODO: перейти на socketserver
PORT = 31338
lvl = 1

class GameServer:

    def __init__(self):
        self.connections = []
        self.server = s.socket(s.AF_INET, s.SOCK_STREAM, s.IPPROTO_TCP)
        self.server.setblocking(False)
        #self.server.settimeout(2)
        self.server.bind(('', PORT))
        self.server.listen(10)
        print('Server bound on port', PORT)

    def receiver(self):
        while 1:
            try:
                return self.server.recvfrom(1024)
            except BlockingIOError:
                time.sleep(0.0001)
                continue

    def serve_forever(self):
        while 1:
            data, addr = self.receiver()
            if addr in self.connections:
                if self.unpack(data, addr):
                    self.spreadToAll(data, addr)
            else:
                if self.server_hello(data, addr):
                    self.connections.append(addr)
                    print('New:\n', self.connections)

    def server_hello(self, data, addr):
        if data == b'HELLO':
            self.server.sendto(struct.pack('i2s', lvl, b'OK'), addr)
            print('Hello:', addr, data)
            if self.receiver()[0] == b'OK':
                return True
        return False

    def unpack(self, packet, p_from):
        if packet == b'END':
            self.connections.remove(p_from)
            print('Disconnecting', p_from)
            return False
        else:
            print(p_from, packet)
            return True
    
    def spreadToAll(self, data, sender=None):
        for client in self.connections:
            if client != sender:
                self.server.sendto(data, client)
        
    def isCliAlive(self): #new thread
        pass
        
    def __del__(self):
        self.server.close()

server = GameServer()
server.serve_forever()