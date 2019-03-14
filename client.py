from API import *
from time import sleep
from world import TWEngine
from threading import Thread
from configs import SCR_SIZE, SERV_IP, SERV_PORT, E_PICKED, MAX_LIFES, E_KILLED, SCR_H_COEFF,\
    PLATFORM_SIZE
from objects import real
from datatypes import OBJECTS_POOL, pics
import socket
import pygame


SERVER_ADDR = (SERV_IP, SERV_PORT)


class TWClient(TWRequest, TWEngine): # клиент тоже наследует игровой движок, но уже с немного другими операциями в игровом цикле
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.sock.setblocking(True)
        TWRequest.__init__(self, self.sock, client=True)
        TWEngine.logger.info('Connecting to ' + str(SERVER_ADDR))
        while True:
            try:
                self.sock.connect(SERVER_ADDR)
                self.api_init() # при успешном подключении запрашиваем свой uid и номер уровня
                data = self._receive()
                if data['method'] == 'INIT': # при успешной инициализации на сервере врубаем графоний
                    self.window = pygame.display.set_mode(SCR_SIZE)
                    self.screen = pygame.Surface(SCR_SIZE)
                    TWEngine.__init__(self, data['nlvl']) # и игровой цикл
                    self.player = self.spawn(real.Player, [10, 2], uid=data['uid'], client=True)
                    break
            except socket.error as err:
                TWEngine.logger.error(str(err))
                sleep(3)
            else:
                sleep(3)
        TWEngine.logger.info(f'Successfully spawned on lvl {data["nlvl"]}')
        self.__wd = self.WatchDog(self)
        Thread(target=self.__update_daemon).start()


    def __update_daemon(self): # принимаем обновления от сервера (тоже в отдельном потоке)
        while self.loop:
            self.api_update(self.player, TW_ACTIONS.LOCATE, 'get_state', upd_pid=False)
            data = self._receive()
            if not data:
                continue
            self.__wd.reset() # обновляем собаку-надсмотрщика
            if data['method'] == 'UPDATE':
                for upd_item in data['updated']:
                    uid = upd_item['uid']
                    obj = OBJECTS_POOL[uid]
                    attrib = upd_item['attrib']
                    if upd_item['action'] == TW_ACTIONS.LOCATE:
                        if not obj: # если пытаемся обновить местоположение не существующего на клиенте объекта, то создаём его
                            try:
                                self.spawn(eval(f"real.{attrib['name']}"), uid=uid, **attrib) # впервые в жизни пригодился eval
                            except KeyError as err:
                                pass
                                #TWEngine.logger.warning('Spawn error %s in %s' % (err, upd_item))
                        else:
                            obj.rect.center = attrib['coords'] # иначе обновляем позицию
                            if attrib['name'] == 'Player':
                                obj.count = attrib['count']
                                obj.velocity = attrib['vel']
                                obj.color = attrib['color']
                                if uid != self.player.uid: # и направления оружия у всех, кроме самих себя
                                    obj.dir = attrib['dir']
                                    try:
                                        if obj.active._name != attrib['wpn']:
                                            obj.switch_weapon(attrib['wpn'])
                                    except AttributeError:
                                        TWEngine.logger.warn('Spawn error in %s (DefBlock, must be Player)', upd_item)
                                else:
                                    obj.lifes = attrib['lifes']
                    elif upd_item['action'] == TW_ACTIONS.REMOVE:
                        obj._destroy()
                    elif upd_item['action'] == TW_ACTIONS.SHOOT:
                        obj.active.shoot(proj_uid=attrib)
                    elif upd_item['action'] == TW_ACTIONS.HOOK:
                        if attrib == 'release':
                            obj.hook.release()
                        else:
                            obj.hook.shoot(proj_uid=attrib)
            elif data['method'] == 'CLOSE':
                self.loop = False
            
            
    def events_handler(self):
        e = pygame.event.poll()
            
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1: # выстрел
                self.api_update(self.player.active, TW_ACTIONS.SHOOT, 'shoot')
            elif e.button == 3: # выстрел хуком
                self.api_update(self.player.hook, TW_ACTIONS.HOOK, 'shoot')
        
        
        if e.type == pygame.MOUSEBUTTONUP:
            if e.button == 3:
                self.api_update(self.player.hook, TW_ACTIONS.HOOK, 'release')
            
        
        if e.type == pygame.KEYDOWN or e.type == pygame.KEYUP:
            self.api_key(e.type, e.key) # нажали или отжали клавишу - сообщаем серверу
    
        
        if e.type == E_PICKED:
            self.api_update(e.target, TW_ACTIONS.REMOVE)
            
            
        if e.type == E_KILLED:
            e.target.respawn()
            
            
        if e.type == pygame.QUIT: # при закрытии клиента завершаем сразу же все потоки
            self.loop = False
            
            
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_LEFT or e.key == pygame.K_a:
                self.player.keydir.x = -1
            elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                self.player.keydir.x = 1
            elif e.key == pygame.K_UP or e.key == pygame.K_SPACE:
                self.player.keydir.y = -1
            elif e.key == pygame.K_ESCAPE:
                self.loop = False
            elif pygame.K_0 <= e.key <= pygame.K_9:
                self.player.switch_weapon(e.key)
                
                
        if e.type == pygame.KEYUP:
            if e.key == pygame.K_LEFT or e.key == pygame.K_a:
                self.player.keydir.x = 0
            elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                self.player.keydir.x = 0
            elif e.key == pygame.K_UP or e.key == pygame.K_SPACE:
                self.player.keydir.y = 0

    
    def HUD(self, surface):
        sb_font = pygame.font.SysFont('Sans Serif', 30)
        player_head_font = pygame.font.SysFont('Sans Serif', 25)
        players = list(filter(lambda x: x._name == 'Player', OBJECTS_POOL))
        for i, player in enumerate(players):
            scoreboard = sb_font.render(f'#{player.uid}:  {player.count}', False, player.color)
            player_head = player_head_font.render(f'#{player.uid}', False, player.color, (250, 250, 250))
            surface.blit(scoreboard, (SCR_SIZE[0]-160, i*20+20))
            surface.blit(player_head, (player.rect.x-20, player.rect.y-25))

        '''for i in range(1, SCR_H_COEFF):
            fnt = sb_font.render(str(i), False, (0, 0, 0))
            surface.blit(fnt, (SCR_SIZE[0]-40, (i-1)*PLATFORM_SIZE-10))
            surface.blit(fnt, (300, (i-1)*PLATFORM_SIZE-10))
            surface.blit(fnt, (600, (i-1)*PLATFORM_SIZE-10))
            surface.blit(fnt, (10, (i-1)*PLATFORM_SIZE-10))'''
            
        if not hasattr(self, 'player'):
            return
        heart_full = pics.get('heart_full')# рисуем шкалу здоровья
        heart_empty = pics.get('heart_empty')
        draw_coeff = 30
        for i in range(MAX_LIFES):
            h_img = heart_full if i+1 <= self.player.lifes else heart_empty
            surface.blit(h_img, (i*draw_coeff, 5))
        
        wpn = self.player.active
        if wpn and wpn.model.proj:
            for i in range(wpn.ammo):
                surface.blit(wpn.model.proj, (i*draw_coeff, 30))


    def _e_cycle_body(self): # клиенту в игровом цикле уже требуется отрисовка
        self.events_handler()
        self.screen.fill(pygame.Color('white'))
        OBJECTS_POOL.update() # поэтому обновляем
        OBJECTS_POOL.fx(self.screen)
        OBJECTS_POOL.draw(self.screen) # и отрисовываем
        self.HUD(self.screen)
        self.window.blit(self.screen, (0,0))
        pygame.display.flip()
    
    
    def close(self):
        try:
            self.api_close()
            self.sock.close()
        except:
            pass
        TWEngine.logger.info('Connection closed')
        if self.loop:
            self.loop = False
    
    
    def __del__(self):
        self.close()
        
    
    class WatchDog(Thread): # простой вачдог, вырубающий клиент игры при потере соединения с сервером
        
        __WD_TIMER_RST = 2
        
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


if __name__ == '__main__':
    TWClient()
