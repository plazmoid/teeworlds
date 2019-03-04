from API import *
from time import sleep
from world import GameEngine
from threading import Thread
from configs import SCR_SIZE, SERV_IP, SERV_PORT, E_PICKED
from objects import real
import socket
import pygame
import utils


SERVER_ADDR = (SERV_IP, SERV_PORT)
OBJECTS_POOL = utils.get_objects_pool()

class TWClient(TWRequest, GameEngine): # клиент тоже наследует игровой движок, но уже с немного другими операциями в игровом цикле
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.sock.setblocking(True)
        TWRequest.__init__(self, self.sock)
        GameEngine.logger.info('Connecting to ' + str(SERVER_ADDR))
        while True:
            try:
                self.sock.connect(SERVER_ADDR)
                self.api_init() # при успешном подключении запрашиваем свой uid и номер уровня
                data = self._receive()
                if data['method'] == 'INIT':
                    self.window = pygame.display.set_mode(SCR_SIZE) # при успешной инициализации на сервере врубаем графоний
                    self.screen = pygame.Surface(SCR_SIZE)
                    GameEngine.__init__(self, data['nlvl']) # и игровой цикл
                    self.player = GameEngine.spawn(real.Player, [0, 0], uid=data['uid'], client=True)
                    #self.player.weaponize('hook') # вооружаем свежесозданного игрока гарпуном
                    break
            except socket.error as err:
                GameEngine.logger.error(str(err))
                sleep(3)
            else:
                sleep(3)
        GameEngine.logger.info(f'Successfully spawned on lvl {data["nlvl"]}')
        self.__wd = self.WatchDog(self)
        Thread(target=self.__update_daemon).start()
        
    
    class WatchDog(Thread): # простой вачдог, вырубающий клиент игры при потере соединения с сервером
        
        __WD_TIMER_RST = 5
        
        def __init__(self, outer):
            super().__init__()
            self.outer = outer
            self.__wd_timer = self.__WD_TIMER_RST
            self.start()
            
        def run(self): # наблюдает в отдельном потоке, потому никому не мешает
            tick = 0.1
            while self.outer.loop:
                while self.__wd_timer > 0:
                    self.__wd_timer -= tick
                    if not self.outer.loop:
                        break
                    #if self.__wd_timer < (self.__WD_TIMER_RST // 2): # если таймер приближается к критической отметке
                    #    try:
                    #        self.outer.api_ping() # последние разы пытаемся пингануть (зачем)
                    #    except: 
                    #        break
                    sleep(tick)
                if self.outer.loop: # и вырубаем клиент
                    self.outer.close()
                    
        def reset(self): # не даём псине отключить нас, когда всё работает
            self.__wd_timer = self.__WD_TIMER_RST
                    
        
    def __update_daemon(self): # принимаем обновления от сервера (тоже в отдельном потоке)
        while self.loop:
            data = self._receive()
            if not data:
                continue
            self.__wd.reset() # обновляем собаку-надсмотрщика
            if data['method'] == 'UPDATE':
                for upd_item in data['updated']:
                    uid = upd_item['uid']
                    if upd_item['action'] == TW_ACTIONS.LOCATE:
                        params = upd_item['params']
                        if not OBJECTS_POOL[uid]: # если пытаемся обновить местоположение не существующего на клиенте объекта, то создаём его
                            GameEngine.spawn(eval(f"real.{params['name']}"), params['coords'], uid=uid) # впервые в жизни пригодился eval
                        else:
                            obj = OBJECTS_POOL[uid]
                            obj.rect.center = params['coords'] # иначе обновляем позицию
                            if params['name'] == 'Player':
                                if uid != self.player.uid: # и направления оружия у всех, кроме самих себя
                                    obj.dir = params['dir']
                                else:
                                    obj.lifes = params['lifes']
                    elif upd_item['action'] == TW_ACTIONS.REMOVE:
                        OBJECTS_POOL.remove_(uid)
            elif data['method'] == 'CLOSE':
                self.loop = False
            
            
    def events_handler(self):
        e = pygame.event.poll()
        if e.type == pygame.KEYDOWN or e.type == pygame.KEYUP: self.api_key(e.key, e.type) # нажали или отжали клавишу - сообщаем серверу
    
        
        if e.type == E_PICKED: #TODO: допилить сердечки
            self.api_update(e.target, TW_ACTIONS.REMOVE)
            
        if e.type == pygame.QUIT: # при закрытии клиента завершаем сразу же все потоки
            self.loop = False
            
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_LEFT or e.key == pygame.K_a:
                self.player.keydir.x = -1
            elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                self.player.keydir.x = 1
            elif e.key == pygame.K_UP or e.key == pygame.K_w:
                self.player.keydir.y = -1
            elif e.key == pygame.K_ESCAPE:
                self.loop = False
                
        if e.type == pygame.KEYUP:
            if e.key == pygame.K_LEFT or e.key == pygame.K_a:
                self.player.keydir.x = 0
            elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                self.player.keydir.x = 0
            elif e.key == pygame.K_UP or e.key == pygame.K_w:
                self.player.keydir.y = 0


    def _e_cycle_body(self): # клиенту в игровом цикле уже требуется отрисовка
        self.events_handler()
        self.screen.fill(pygame.Color('white'))
        OBJECTS_POOL.update() # поэтому обновляем
        OBJECTS_POOL.draw(self.screen) # и отрисовываем
        self.window.blit(self.screen, (0,0))
        OBJECTS_POOL.custom_draw(self.window) # и ещё раз отрисовываем что-нибудь поверх, полоску здоровья ту же
        pygame.display.flip()
    
    
    def close(self):
        try:
            self.api_close()
            self.sock.close()
        except:
            pass
        GameEngine.logger.info('Connection closed')
        if self.loop:
            self.loop = False
    
    
    def __del__(self):
        self.close()


if __name__ == '__main__':
    TWClient()
