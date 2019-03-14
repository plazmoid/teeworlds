from threading import Thread, Lock
from time import sleep
from API import *
from socketserver import BaseRequestHandler, ThreadingTCPServer
from world import TWEngine
from objects import real
from configs import E_PICKED, E_KILLED
from random import randint
from datatypes import OBJECTS_POOL
import pygame


CLIENTS = {} # {TWObject: TWServerHandler}
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
                self.net_spawn()
            elif data['method'] == 'CLOSE':
                self.net_destroy()
            elif data['method'] == 'KEY':
                self.keys_handler(data)
            elif data['method'] == 'UPDATE':
                self.updater(data)
                
                
    def updater(self, data):
        for upd_item in data['updated']:
            if upd_item['action'] == TW_ACTIONS.LOCATE:
                if upd_item['uid'] == self.player.uid:
                    params = upd_item['attrib']
                    self.player.dir = params['dir']
            elif upd_item['action'] == TW_ACTIONS.REMOVE:
                serv.remove_object(upd_item['uid'])
            elif upd_item['action'] == TW_ACTIONS.SHOOT:
                if self.player.active.ammo > 0:
                    self.player.active.shoot(proj_uid=upd_item['attrib'])
                    serv.broadcast('api_update', self.player.uid, TW_ACTIONS.SHOOT, attrib=upd_item['attrib'], exclude=self)
            elif upd_item['action'] == TW_ACTIONS.HOOK:
                if upd_item['attrib'] == 'release':
                    pr_id = self.player.hook.release()
                else:
                    pr_id = self.player.hook.shoot(proj_uid=upd_item['attrib'])
                serv.broadcast('api_update', self.player.uid, TW_ACTIONS.HOOK, attrib=pr_id, exclude=self)
                
    
    def player_reset(self):            
        self.player = serv.spawn(real.Player, [10, 2])
        with lock:
            CLIENTS[self.player] = self # добавляем себя в глобальную таблицу клиентов
    

    def net_spawn(self):
        self.player_reset()
        self.api_init(serv.lvl) # только созданному игроку отправляется его uid (берётся в TWRequest) и номер загруженного на сервере уровня
        TWEngine.logger.info(f'Connected player #{self.player.uid} from {self.request.getpeername()}')
        Thread(target=self.__update_daemon).start()
        
        
    def __update_daemon(self): # собираем обновления от всех других игроков
        while self.loop:
            self.api_update(serv.get_updateable_objects(), TW_ACTIONS.LOCATE, 'get_state')
            sleep(0.03)


    def keys_handler(self, data): # игрок на клиенте перемещается вместе с игроком на сервере не дожидаясь возможно запоздалого ответа от сервера,
        key = data['key'] # соединение лишь синхронизирует их
        ktype = data['keytype']
        if ktype == pygame.KEYDOWN:
            if key == pygame.K_LEFT or key == pygame.K_a:
                self.player.keydir.x = -1
            elif key == pygame.K_RIGHT or key == pygame.K_d:
                self.player.keydir.x = 1
            elif key == pygame.K_UP or key == pygame.K_SPACE:
                self.player.keydir.y = -1
            elif pygame.K_0 <= key <= pygame.K_9:
                self.player.switch_weapon(key)
            elif key == pygame.K_u:
                self.player.rect.center = (100, 20)
     
        elif ktype == pygame.KEYUP:
            if key == pygame.K_LEFT or key == pygame.K_a:
                self.player.keydir.x = 0
            elif key == pygame.K_RIGHT or key == pygame.K_d:
                self.player.keydir.x = 0
            elif key == pygame.K_UP or key == pygame.K_SPACE:
                self.player.keydir.y = 0
        

    def net_destroy(self):
        with lock: # потокобезопасно удаляем игрока из всех таблиц
            del CLIENTS[self.player]
        serv.broadcast('api_update', self.player, TW_ACTIONS.REMOVE) # и говорим всем, что он отвалился
        self.player._destroy()
        self.loop = False # завершаем для этого игрока игровой цикл
        TWEngine.logger.info(f'Player #{self.player.uid} disconnected')
        
        

class TWServer(ThreadingTCPServer, TWEngine): # игровой сервер помимо ожидания подключений крутит и игровой цикл
    
    def __init__(self, *args, nlvl):
        ThreadingTCPServer.__init__(self, *args)
        TWEngine.__init__(self, nlvl=nlvl)
        Thread(target=self.__temp_spawner).start() # тестовый спавнер (зачем)
        
        
    def _e_cycle_body(self): # в цикле сервера не нужно ничего отрисовывать, просто обрабатываем события и обновляем состояния игровых объектов
        self.events_handler()
        OBJECTS_POOL.update()
        
    
    def events_handler(self):
        e = pygame.event.poll()
        if e.type == E_PICKED: # кто-то что-то хапнул на карте
            self.remove_object(e.target)
        elif e.type == E_KILLED: # кто-то кого-то убил
            #self.broadcast('api_update', e.target, TW_ACTIONS.REMOVE) # и говорим всем, что он отвалился
            e.author.count += 1
            e.target.rect.center = (100, 20)
            e.target.respawn()
        
    
    def get_updateable_objects(self): # получить все обновляемые объекты
        return list(filter(lambda obj: obj.updateable, OBJECTS_POOL))
        
        
    def remove_object(self, obj): # удаление теоретически любого объекта с дальнейшей рассылкой об удалении
        OBJECTS_POOL.remove_(obj)
        serv.broadcast('api_update', obj, TW_ACTIONS.REMOVE)

        
    def broadcast(self, method, *args, exclude=None, **kwargs):
        for client in CLIENTS.values():
            if client != exclude:
                try:
                    getattr(client, method)(*args, **kwargs)
                except BrokenPipeError:
                    client.net_destroy()
            
        
    def __temp_spawner(self):
        while True:
            x = randint(0, 35)
            y = randint(0, 15)
            for i in range(randint(1, 5)):
                self.spawn(real.Heart, [x + i, y])
            sleep(randint(8, 15))
    

if __name__ == '__main__':
    TWServer.allow_reuse_address = True
    serv = TWServer(('', 31337), TWServerHandler, nlvl=1)
    Thread(target=serv.serve_forever).start()
