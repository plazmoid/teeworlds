import threading
import World
import Objects
import random
import pygame
from API import TW_API, TWRequest
from socketserver import BaseRequestHandler, ThreadingTCPServer

CLIENTS = {}

class TWServerHandler(BaseRequestHandler, TWRequest):

#     def __init__(self, *args):
#         BaseRequestHandler.__init__(self, *args)

    def handle(self):
        TWRequest.__init__(self, self.request)
        while True:
            data = self._receive()
            if data['method'] == 'INIT':
                self.new_player()
            elif data['method'] == 'UPDATE':
                self.updater()
            elif data['method'] == 'UPDATE':
                self.keys_handler(data['key'], data['keytype'])

    def new_player(self):
        random.seed()
        while not self.session:
            self.session = random.randint(1, 255)
            if self.session not in CLIENTS:
                break
        CLIENTS.update({self.session: World.create_player()})
        self._request(TW_API.INIT)
        
    def updater(self):
        self._request(TW_API.UPDATE, updated={int(k): v.getXY() for k, v in CLIENTS.items()})

    def keys_handler(self, key, ktype):
        if key == pygame.K_LEFT or key == pygame.K_a:
            CLIENTS[self.session].keydir[0] = -1
        if ktype == pygame.KEYDOWN:
            if key == pygame.K_LEFT or key == pygame.K_a:
                CLIENTS[self.session].keydir[0] = -1
            elif key == pygame.K_RIGHT or key == pygame.K_d:
                CLIENTS[self.session].keydir[0] = 1
            elif key == pygame.K_UP or key == pygame.K_w:
                CLIENTS[self.session].keydir[1] = -1
     
        elif ktype == pygame.KEYUP:
            if key == pygame.K_LEFT or key == pygame.K_a:
                CLIENTS[self.session].keydir[0] = 0
            elif key == pygame.K_RIGHT or key == pygame.K_d:
                CLIENTS[self.session].keydir[0] = 0
            elif key == pygame.K_UP or key == pygame.K_w:
                CLIENTS[self.session].keydir[1] = 0

    def __del__(self):
        CLIENTS.pop(self.session)


class TWThreadingTCPServer(ThreadingTCPServer):
    def __init__(self, *args):
        ThreadingTCPServer.__init__(self, *args)
        threading.Thread(target=self.mainloop).start()
        
    def mainloop(self):
        level = World.LevelBuilder()
        level.build(1)
        while True:
            Objects.OBJECTS_POOL.update()
            pygame.time.wait(12)
        

ThreadingTCPServer.allow_reuse_address = True
server = ThreadingTCPServer(('0.0.0.0', 31337), TWServerHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()
