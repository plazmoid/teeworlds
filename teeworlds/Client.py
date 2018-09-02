import socket
import threading
import Objects
import World
import pygame
from API import TW_API, TWRequest
from time import sleep

SERVER_ADDR = ('0.0.0.0', 31337)
ENTITIES = {}

class TWClient(TWRequest):    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TWRequest.__init__(self, self.sock)
        print('Establishing connection...')
        while not self.session:
            try:
                self.sock.connect(SERVER_ADDR)
                self._request(TW_API.INIT)
                self.session = self._receive()['session']
            except socket.error as err:
                print('wtf:', str(err))
                sleep(1)
                continue
        print('Wow, such conexion')
        threading.Thread(target=self.updater).start()
        ENTITIES.update({self.session: World.create_player()})
        self.mainloop()
        
    def send_keys(self, key, keytype):
        self._request(TW_API.KEY, key=key, keytype=keytype)
        
    def updater(self):
        while True:
            self._request(TW_API.UPDATE, updated='')
            for k,v in self._receive()['updated'].items():
                c = v.split('|')
                if k not in ENTITIES:
                    ENTITIES[k] = World.create_player([int(c[0]), int(c[1])])
                else:
                    ENTITIES[k].rect.x = int(c[0])
                    ENTITIES[k].rect.y = int(c[1])
            sleep(0.15)
            
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
        self.loop = True
        while self.loop:
            #pygame.display.set_caption('dir: %s, xy: %s, vel: %s, %s' % (hero.dir, [hero.rect.x, hero.rect.y], [hero.xvel, round(hero.yvel, 2)], hero.onGround))
            self.events_handler()
            screen.fill(pygame.Color('white'))
            Objects.OBJECTS_POOL.update()
            Objects.OBJECTS_POOL.draw(screen)
            window.blit(screen, (0,0))
            pygame.display.flip()
            pygame.time.wait(12)
    
    def __del__(self):
        self.sock.close()


TWClient()
