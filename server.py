from threading import Thread, Lock
from time import sleep
from API import *
from socketserver import BaseRequestHandler, ThreadingTCPServer
from world import GameEngine
from objects import real
from configs import E_PICKED
from random import randint
import pygame
import datatypes



CLIENTS = {} # {наследник TWObject: сущность TWServerHandler}
OBJECTS_POOL = datatypes.get_objects_pool()
lock = Lock()

class TWServerHandler(BaseRequestHandler, TWRequest): # обработчик одного соединения, крутится в отдельном потоке

    def handle(self):
        TWRequest.__init__(self, self.request) # всё лезущее в сеть наследуется от TWRequest и использует его методы, чтобы лезть правильно
        self.loop = True
        while self.loop:
            try:
                data = self._receive()
            except ConnectionResetError:
                try:
                    self.remove_player() # игрок отпал - вырубаем его на сервере с последующей рассылкой
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
            #elif data['method'] == 'INTERACT':
            #    serv.remove_object(data['target']) # перепилить это под взаимодействия игроков
            elif data['method'] == 'UPDATE':
                self.updater(data)
                
                
    def updater(self, data):
        for upd_item in data['updated']:
            if upd_item['action'] == TW_ACTIONS.LOCATE:
                if upd_item['uid'] == self.player.uid:
                    params = upd_item['params']
                    #self.player.rect.center = params['coords'] # иначе обновляем позицию
                    self.player.dir = params['dir']
                    self.player.active = params['wpn']
                    #serv.broadcast('api_update', self.player, TW_ACTIONS.LOCATE, 'get_state') # когда клиент ну очень хочет сам обновиться
            elif upd_item['action'] == TW_ACTIONS.REMOVE:
                serv.remove_object(upd_item['uid'])
                

    def new_player(self):
        self.player = GameEngine.spawn(real.Player, [10, 2])
        self.api_init(GameEngine.curr_level) # только созданному игроку отправляется его uid (берётся в TWRequest) и номер загруженного на сервере уровня
        with lock:
            CLIENTS[self.player] = self # добавляем себя в глобальную таблицу клиентов
        GameEngine.logger.info(f'Connected player #{self.player.uid}')
        serv.broadcast('api_update', self.player, TW_ACTIONS.LOCATE, 'get_state') # широковещаем всем игрокам, что мы родились
        Thread(target=self.__update_daemon).start()
        
        
    def __update_daemon(self): # собираем обновления от всех других игроков
        while self.loop:
            self.api_update(list(CLIENTS) + serv.get_dynamic_objects(), TW_ACTIONS.LOCATE, 'get_state')
            sleep(0.03)


    def keys_handler(self, data): # игрок на клиенте перемещается вместе с игроком на сервере не дожидаясь возможно запоздалого ответа от сервера,
        key = data['key'] # соединение лишь синхронизирует их
        ktype = data['keytype']
        if ktype == pygame.KEYDOWN:
            if key == pygame.K_LEFT or key == pygame.K_a:
                self.player.keydir.x = -1
            elif key == pygame.K_RIGHT or key == pygame.K_d:
                self.player.keydir.x = 1
            elif key == pygame.K_UP or key == pygame.K_w:
                self.player.keydir.y = -1
     
        elif ktype == pygame.KEYUP:
            if key == pygame.K_LEFT or key == pygame.K_a:
                self.player.keydir.x = 0
            elif key == pygame.K_RIGHT or key == pygame.K_d:
                self.player.keydir.x = 0
            elif key == pygame.K_UP or key == pygame.K_w:
                self.player.keydir.y = 0
        

    def remove_player(self):
        with lock: # потокобезопасно удаляем игрока из всех таблиц
            del CLIENTS[self.player]
        OBJECTS_POOL.remove_(self.player) # а OBJECTS_POOL безопасен уже внутри реализации
        self.loop = False # завершаем для этого игрока игровой цикл
        serv.broadcast('api_update', self.player, TW_ACTIONS.REMOVE) # и говорим всем, что он отвалился
        GameEngine.logger.info(f'Player #{self.player.uid} disconnected')
        



class TWServer(ThreadingTCPServer, GameEngine): # игровой сервер помимо ожидания подключений крутит и игровой цикл
    
    def __init__(self, *args, nlvl=1):
        ThreadingTCPServer.__init__(self, *args)
        GameEngine.__init__(self, nlvl=nlvl)
        Thread(target=self.__temp_spawner).start() # тестовый спавнер (зачем)
        
        
    def _e_cycle_body(self): # в цикле сервера не нужно ничего отрисовывать, просто обрабатываем события и обновляем состояния игровых объектов
        self.events_handler()
        OBJECTS_POOL.update()
        
    
    def events_handler(self):
        e = pygame.event.poll()
        if e.type == E_PICKED: # кто-то что-то хапнул на карте
            
            self.remove_object(e.target)
        
    
    def get_dynamic_objects(self): # получить все динамические (созданные через GameEngine.spawn) объекты для их обновления и рассылки обновлений всем клиентам
        return list(filter(lambda obj: obj.pickable, OBJECTS_POOL))
        
        
    def remove_object(self, obj): # удаление теоретически любого объекта с дальнейшей рассылкой об удалении
        OBJECTS_POOL.remove_(obj)
        serv.broadcast('api_update', obj, TW_ACTIONS.REMOVE)

        
    def broadcast(self, method, *args, **kwargs):
        for client in CLIENTS.values():
            getattr(client, method)(*args, **kwargs)
            
        
    def __temp_spawner(self):
        while True:
            GameEngine.spawn(real.Heart, [randint(0, 25), randint(0, 20)])
            sleep(randint(8, 15))
    

ThreadingTCPServer.allow_reuse_address = True
serv = TWServer(('', 31337), TWServerHandler, nlvl=1)
Thread(target=serv.serve_forever).start()
