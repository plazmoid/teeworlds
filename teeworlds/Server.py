from threading import Thread, Lock
from Objects import OBJECTS_POOL
from API import *
from socketserver import BaseRequestHandler, ThreadingTCPServer
import World
import random
import pygame
import logging

CLIENTS = {}
lock = Lock()

class TWServerHandler(BaseRequestHandler, TWRequest):

    def handle(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        TWRequest.__init__(self, self.request)
        self.handle_loop = True
        while self.handle_loop:
            data = self._receive()
            if not data:
                continue
            if data['method'] == 'INIT':
                self.new_player()
            elif data['method'] == 'CLOSE':
                self.remove_player()
            elif data['method'] == 'UPDATE':
                self.updater()
            elif data['method'] == 'KEY':
                self.keys_handler(data['key'], data['keytype'])

    def new_player(self):
        random.seed()
        while not self.session:
            self.session = random.randint(1, 255)
            if self.session not in map(lambda x: x.session, CLIENTS.keys()):
                break
        try:
            lock.acquire()
            CLIENTS.update({self: World.create_player()})
        finally:
            lock.release()
        self.logger.info('Connected player with id: {}'.format(self.session))
        self._request(TW_API.INIT)
        
    def updater(self):
        updated = [TW_API.UPD_PARAMS(uid=k.session, action=TW_ACTIONS.LOCATION, params=v.getXY()) for k, v in CLIENTS.items()]
        self._request(TW_API.UPDATE, updated=updated)

    def keys_handler(self, key, ktype):
        if key == pygame.K_LEFT or key == pygame.K_a:
            CLIENTS[self].keydir[0] = -1
        if ktype == pygame.KEYDOWN:
            if key == pygame.K_LEFT or key == pygame.K_a:
                CLIENTS[self].keydir[0] = -1
            elif key == pygame.K_RIGHT or key == pygame.K_d:
                CLIENTS[self].keydir[0] = 1
            elif key == pygame.K_UP or key == pygame.K_w:
                CLIENTS[self].keydir[1] = -1
     
        elif ktype == pygame.KEYUP:
            if key == pygame.K_LEFT or key == pygame.K_a:
                CLIENTS[self].keydir[0] = 0
            elif key == pygame.K_RIGHT or key == pygame.K_d:
                CLIENTS[self].keydir[0] = 0
            elif key == pygame.K_UP or key == pygame.K_w:
                CLIENTS[self].keydir[1] = 0
                
    def remove_player(self):
        try:
            lock.acquire()
            OBJECTS_POOL.remove(CLIENTS[self])
            CLIENTS.pop(self)
        finally:
            lock.release()
        self.handle_loop = False
        updated = [TW_API.UPD_PARAMS(uid=self.session, action=TW_ACTIONS.REMOVE, params='')]
        self.broadcast(TW_API.UPDATE, updated=updated)
        self.logger.info('Player #{} disconnected'.format(self.session))
        
    def broadcast(self, *args, **kwargs):
        for client in CLIENTS:
            if client != self:
                client._request(*args, **kwargs)


class TWThreadingTCPServer(ThreadingTCPServer):
    def __init__(self, *args):
        ThreadingTCPServer.__init__(self, *args)
        Thread(target=self.mainloop).start()
        
    def mainloop(self):
        level = World.LevelBuilder()
        level.build(1)
        while True:
            OBJECTS_POOL.update()
            pygame.time.wait(12)
        

ThreadingTCPServer.allow_reuse_address = True
server = TWThreadingTCPServer(('0.0.0.0', 31337), TWServerHandler)
Thread(target=server.serve_forever).start()
