import socket as s
import struct
import threading

SERV_PORT = 31338
SERV_IP = 'localhost'

class Receiver(threading.Thread):
    
    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.__recvbuf = None
        self.newdata = False
        
    def store(self, data): #мб в дальнейшем поменять на FIFO
        self.__recvbuf = data
        self.newdata = True

    def get(self):
        if self.newdata:
            self.newdata = False
            return self.__recvbuf
        return False
    
    def run(self):
        while 1:
            if self.sock._closed:
                break
            data, addr = self.sock.recvfrom(1024)
            if addr == (SERV_IP, SERV_PORT):
                print('RECEIVED:', data)
                self.store(data)

class GameClient:

    def __init__(self):
        self.client = s.socket(s.AF_INET, s.SOCK_DGRAM, s.IPPROTO_UDP)
        #self.client.settimeout(3)
        self.level = 0
        self.receiver = Receiver(self.client)
            
    def mainloop(self):
        while 1:
            if self.client_hello():
                print('Соединение установлено!')
                break
        #вставить обработчики нажатия клавиш
        
    def sender(self, bindata):
        self.client.sendto(bindata, (SERV_IP, SERV_PORT))
        
    def client_hello(self):
        self.sender(b'HELLO')
        if not self.receiver.isAlive():
            self.receiver.start()
        while 1:
            if self.receiver.newdata:
                data = struct.unpack('i2s', self.receiver.get())
                break
        if data[1] == b'OK':
            self.level = data[0]
            self.sender(b'OK')
            return True
        
    def __del__(self):
        self.sender(b'END')
        self.client.close()
        
client = GameClient()
client.mainloop()