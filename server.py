from threading import Thread, Lock
from time import sleep
from API import *
from socketserver import BaseRequestHandler, ThreadingTCPServer
from world import GameEngine
from objects import real
from configs import E_PICKED
import pygame
import utils


CLIENTS = {}
OBJECTS_POOL = utils.get_objects_pool()
lock = Lock()

class TWServerHandler(BaseRequestHandler, TWRequest): # разделить логику на соединение и обработку

    def handle(self):
        TWRequest.__init__(self, self.request)
        self.loop = True
        while self.loop:
            try:
                data = self._receive()
            except ConnectionResetError:
                try:
                    self.remove_player()
                except:
                    continue
            if not data:
                continue
            if data['method'] == 'INIT':
                self.new_player()
            elif data['method'] == 'CLOSE':
                self.remove_player()
            elif data['method'] == 'KEY':
                self.keys_handler(data)
            elif data['method'] == 'PING':
                self.api_ping()
            #elif data['method'] == 'UPDATE':
                #self.updater()
                

    def new_player(self):
        self.player = GameEngine.spawn(real.Player, [100, 200])
        self.api_init(GameEngine.curr_level)
        with lock:
            CLIENTS[self.player] = self
        GameEngine.logger.info(f'Connected player #{self.player.uid}')
        Thread(target=self.__updater).start()
        
        
    def __updater(self):
        while self.loop:
            self.api_update(list(CLIENTS) + serv.get_dynamic_objects(), TW_ACTIONS.LOCATE, 'getXY')
            sleep(0.01)


    def keys_handler(self, data):
        key = data['key']
        ktype = data['keytype']
        if key == pygame.K_LEFT or key == pygame.K_a:
            self.player.keydir[0] = -1
        if ktype == pygame.KEYDOWN:
            if key == pygame.K_LEFT or key == pygame.K_a:
                self.player.keydir[0] = -1
            elif key == pygame.K_RIGHT or key == pygame.K_d:
                self.player.keydir[0] = 1
            elif key == pygame.K_UP or key == pygame.K_w:
                self.player.keydir[1] = -1
     
        elif ktype == pygame.KEYUP:
            if key == pygame.K_LEFT or key == pygame.K_a:
                self.player.keydir[0] = 0
            elif key == pygame.K_RIGHT or key == pygame.K_d:
                self.player.keydir[0] = 0
            elif key == pygame.K_UP or key == pygame.K_w:
                self.player.keydir[1] = 0
        
        
    def remove_object(self, obj):
        OBJECTS_POOL.remove_(obj)
        self.broadcast(self.api_update(obj, TW_ACTIONS.REMOVE, constructOnly=True))


    def remove_player(self):
        with lock:
            del CLIENTS[self.player]
        OBJECTS_POOL.remove_(self.player)
        self.loop = False
        self.broadcast(self.api_update(self.player, TW_ACTIONS.REMOVE, constructOnly=True))
        GameEngine.logger.info(f'Player #{self.player.uid} disconnected')
        
        
    def broadcast(self, req):
        for client in CLIENTS.values():
            print(f'REQ {req} ||| {client}')
            client.req()
                


class TWServer(ThreadingTCPServer, GameEngine):
    
    def __init__(self, *args, nlvl=1):
        ThreadingTCPServer.__init__(self, *args)
        GameEngine.__init__(self, nlvl=nlvl)
        Thread(target=self.__temp_spawner).start()
        
        
    def _e_cycle_body(self):
        self.events_handler()
        OBJECTS_POOL.update()
        
    
    def events_handler(self):
        e = pygame.event.poll()
        if e.type == E_PICKED:
            print(vars(CLIENTS[e.author]))
            CLIENTS[e.author].remove_object(e.target)
        
        
    def get_dynamic_objects(self):
        return list(filter(lambda obj: obj.pickable, OBJECTS_POOL))
        
        
    def __temp_spawner(self):
        GameEngine.spawn(real.Heart, [160, 260])
        GameEngine.spawn(real.Heart, [200, 260])
        sleep(5)
        GameEngine.spawn(real.Heart, [240, 260])
    


ThreadingTCPServer.allow_reuse_address = True
serv = TWServer(('0.0.0.0', 31337), TWServerHandler, nlvl=1)
Thread(target=serv.serve_forever).start()
