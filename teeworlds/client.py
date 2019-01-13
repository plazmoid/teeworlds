from objects import OBJECTS_POOL
from API import *
from time import sleep
from world import GameEngine, SCR_SIZE
from threading import Thread
import socket
import pygame

SERV_IP = '127.0.0.1' #'90.157.107.41'
SERV_PORT = 31337
SERVER_ADDR = (SERV_IP, SERV_PORT)
ENTITIES = {}


class TWClient(TWRequest, GameEngine):
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TWRequest.__init__(self, self.sock)
        GameEngine.logger.info('Connecting to ' + str(SERVER_ADDR))
        while not self.session:
            try:
                self.sock.connect(SERVER_ADDR)
                self.api_init()
                data = self._receive()
                self.session = data['session']
                self.window = pygame.display.set_mode(SCR_SIZE)
                self.screen = pygame.Surface(SCR_SIZE)
                GameEngine.__init__(self, data['nlvl'])
            except socket.error as err:
                GameEngine.logger.error(str(err))
                sleep(3)
                continue
        GameEngine.logger.info(f'Successfully spawned on lvl {data["nlvl"]}')
        Thread(target=self._updater).start()
        
    def _updater(self):
        while self.loop:
            sleep(0.01)
            data = self._receive()
            if not data:
                continue
            for upd_item in data['updated']:
                uid = upd_item['uid']
                if upd_item['action'] == TW_ACTIONS.LOCATE:
                    params = upd_item['params']
                    if uid not in ENTITIES:
                        ENTITIES[uid] = GameEngine.createPlayer(params)
                    else:
                        ENTITIES[uid].rect.x = params[0]
                        ENTITIES[uid].rect.y = params[1]
                elif upd_item['action'] == TW_ACTIONS.REMOVE:
                    OBJECTS_POOL.remove(ENTITIES[uid])
                    ENTITIES.pop(uid)
            
    def events_handler(self):
        e = pygame.event.poll()
        if e.type == pygame.QUIT:
            self.loop = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.loop = False
        if e.type == pygame.KEYDOWN or e.type == pygame.KEYUP:
            self.api_key(e.key, e.type)
            
    def _cycle_body(self):
        self.events_handler()
        self.screen.fill(pygame.Color('white'))
        OBJECTS_POOL.update()
        OBJECTS_POOL.draw(self.screen)
        self.window.blit(self.screen, (0,0))
        pygame.display.flip()
    
    def __del__(self):
        self.api_close()
        self.sock.close()


TWClient()
