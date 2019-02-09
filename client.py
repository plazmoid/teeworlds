from API import *
from time import sleep
from world import GameEngine
from threading import Thread
from configs import SCR_SIZE, SERV_IP, SERV_PORT
from objects import real
import socket
import pygame
import utils


SERVER_ADDR = (SERV_IP, SERV_PORT)
OBJECTS_POOL = utils.get_objects_pool()

class TWClient(TWRequest, GameEngine):
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TWRequest.__init__(self, self.sock)
        GameEngine.logger.info('Connecting to ' + str(SERVER_ADDR))
        while True:
            try:
                self.sock.connect(SERVER_ADDR)
                self.api_init()
                data = self._receive()
                if data['method'] == 'INIT':
                    self.window = pygame.display.set_mode(SCR_SIZE)
                    self.screen = pygame.Surface(SCR_SIZE)
                    GameEngine.__init__(self, data['nlvl'])
                    self.player = GameEngine.spawn(real.Player, [100, 200], uid=data['uid'])
                    break
            except socket.error as err:
                GameEngine.logger.error(str(err))
                sleep(3)
            else:
                sleep(3)
        GameEngine.logger.info(f'Successfully spawned on lvl {data["nlvl"]}')
        self.__wd = self.WatchDog(self)
        Thread(target=self.__updater).start()
        
    
    class WatchDog(Thread):
        
        def __init__(self, outer):
            super().__init__()
            self.outer = outer
            self.__WD_TIMER_RST = 5
            self.__wd_timer = self.__WD_TIMER_RST
            self.ping_att = 2
            self.start()
            
        def run(self):
            tick = 0.1
            while self.outer.loop:
                while self.__wd_timer > 0:
                    self.__wd_timer -= tick
                    if not self.outer.loop:
                        break
                    if self.__wd_timer < (self.__WD_TIMER_RST // 2):
                        try:
                            self.outer.api_ping()
                        except: 
                            break
                    sleep(tick)
                if self.outer.loop:
                    self.outer.close()
                    
        def reset(self):
            self.__wd_timer = self.__WD_TIMER_RST
                    
        
    def __updater(self):
        while self.loop:
            data = self._receive() # select/poll
            if not data:
                continue
            self.__wd.reset()
            if data['method'] == 'UPDATE':
                for upd_item in data['updated']:
                    uid = upd_item['uid']
                    if upd_item['action'] == TW_ACTIONS.LOCATE:
                        params = upd_item['params']
                        if not OBJECTS_POOL[uid]:
                            GameEngine.spawn(eval(f'real.{params[0]}'), params[1:], uid=uid)
                            #GameEngine.logger.info(f'Spawned {ob}\n{ob.uid}\n{uid}')
                        else:
                            OBJECTS_POOL[uid].rect.x = params[1]
                            OBJECTS_POOL[uid].rect.y = params[2]
                    elif upd_item['action'] == TW_ACTIONS.REMOVE:
                        GameEngine.logger.info(f'Removed {uid}')
                        OBJECTS_POOL.remove_(uid)
            elif data['method'] == 'CLOSE':
                self.loop = False
            
            
    def events_handler(self):
        e = pygame.event.poll()
        if e.type == pygame.QUIT:
            self.loop = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.loop = False
        if e.type == pygame.KEYDOWN or e.type == pygame.KEYUP:
            self.api_key(e.key, e.type)


    def _e_cycle_body(self):
        self.events_handler()
        self.screen.fill(pygame.Color('white'))
        OBJECTS_POOL.update()
        OBJECTS_POOL.draw(self.screen)
        self.window.blit(self.screen, (0,0))
        pygame.display.flip()
    
    
    def close(self):
        try:
            self.api_close()
            self.sock.close()
        except:
            pass
        if self.loop:
            GameEngine.logger.info('Connection closed')
            self.loop = False
    
    
    def __del__(self):
        self.close()


TWClient()
