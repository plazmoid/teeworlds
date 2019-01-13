from threading import Thread, Lock
from time import sleep
from objects import OBJECTS_POOL
from API import *
from socketserver import BaseRequestHandler, ThreadingTCPServer
from world import GameEngine
import random
import pygame

CLIENTS = {}
lock = Lock()

class TWServerHandler(BaseRequestHandler, TWRequest):

    def handle(self):
        TWRequest.__init__(self, self.request)
        self.loop = True
        while self.loop:
            data = self._receive()
            if not data:
                continue
            if data['method'] == 'INIT':
                self.new_player()
            elif data['method'] == 'CLOSE':
                self.remove_player()
            #elif data['method'] == 'UPDATE':
                #self.updater()
            elif data['method'] == 'KEY':
                self.keys_handler(data)

    def new_player(self):
        random.seed()
        while not self.session:
            self.session = random.randint(0, 255)
            if self.session not in map(lambda x: x.session, CLIENTS.keys()):
                break
        self.api_init(GameEngine.curr_level)
        with lock:
            CLIENTS.update({self: GameEngine.createPlayer()})
        GameEngine.logger.info(f'Connected player #{self.session}')
        Thread(target=self._updater).start()
        
    def _updater(self):
        while self.loop:
            self.api_update(list(CLIENTS.items()), TW_ACTIONS.LOCATE, 'getXY')
            sleep(0.01)

    def keys_handler(self, data):
        key = data['key']
        ktype = data['keytype']
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
        with lock:
            OBJECTS_POOL.remove(CLIENTS[self])
            CLIENTS.pop(self)
        self.loop = False
        self.broadcast(self.api_update(self.session, TW_ACTIONS.REMOVE, constructOnly=True))
        GameEngine.logger.info(f'Player #{self.session} disconnected')
        
    def broadcast(self, req):
        for client in CLIENTS:
            if client != self:
                client.req()
                
    def __del__(self):
        self.broadcast(self.api_update(CLIENTS.items(), TW_ACTIONS.REMOVE, constructOnly=True))


class TWServer(ThreadingTCPServer, GameEngine):
    
    def __init__(self, *args, nlvl=1):
        ThreadingTCPServer.__init__(self, *args)
        GameEngine.__init__(self, nlvl=nlvl)
        
    def _cycle_body(self):
        OBJECTS_POOL.update()
        

ThreadingTCPServer.allow_reuse_address = True
server = TWServer(('0.0.0.0', 31337), TWServerHandler, nlvl=1)
Thread(target=server.serve_forever).start()
