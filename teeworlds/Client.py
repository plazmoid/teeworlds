import socket
import threading
import World
import pygame
from Objects import OBJECTS_POOL
from API import *
from time import sleep

SERVER_ADDR = ('90.157.107.41', 31337)
ENTITIES = {}

class TWClient(TWRequest):    
    def __init__(self):
        self.loop = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TWRequest.__init__(self, self.sock)
        print('Establishing conexion...')
        while not self.session:
            try:
                self.sock.connect(SERVER_ADDR)
                self._request(TW_API.INIT)
                self.session = self._receive()['session']
            except socket.error as err:
                print('wtf:', str(err))
                sleep(1)
                continue
        print('Sucks ass')
        threading.Thread(target=self._updater).start()
        self.mainloop()
        
    def send_keys(self, key, keytype):
        self._request(TW_API.KEY, key=key, keytype=keytype)
        
    def _updater(self):
        while self.loop:
            self._request(TW_API.UPDATE, updated='')
            data = self._receive()
            for upd_item in data['updated']:
                uid = upd_item['uid']
                if upd_item['action'] == TW_ACTIONS.LOCATION:
                    c = upd_item['params']
                    if uid not in ENTITIES:
                        ENTITIES[uid] = World.create_player([c[0], c[1]])
                    else:
                        ENTITIES[uid].rect.x = c[0]
                        ENTITIES[uid].rect.y = c[1]
                elif upd_item['action'] == TW_ACTIONS.REMOVE:
                    OBJECTS_POOL.remove(ENTITIES[uid])
                    ENTITIES.pop(uid)
                    
            sleep(0.01)
            
    def events_handler(self):
        e = pygame.event.poll()
        if e.type == pygame.QUIT:
            self.loop = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.loop = False
        if e.type == pygame.KEYDOWN or e.type == pygame.KEYUP:
            self.send_keys(e.key, e.type)
            
    def mainloop(self):
        level = World.LevelBuilder()
        level.build(1)
        window = pygame.display.set_mode(World.SCR_SIZE)
        screen = pygame.Surface(World.SCR_SIZE)
        while self.loop:
            #pygame.display.set_caption('dir: %s, xy: %s, vel: %s, %s' % (hero.dir, [hero.rect.x, hero.rect.y], [hero.xvel, round(hero.yvel, 2)], hero.onGround))
            self.events_handler()
            screen.fill(pygame.Color('white'))
            OBJECTS_POOL.update()
            OBJECTS_POOL.draw(screen)
            window.blit(screen, (0,0))
            pygame.display.flip()
            pygame.time.wait(12)
    
    def __del__(self):
        self._request(TW_API.CLOSE)
        self.sock.close()


TWClient()
