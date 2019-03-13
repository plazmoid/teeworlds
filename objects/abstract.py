# Тут свалены абстракции, т.е. предметы, которые создавать бессмысленно, но их каркас используется наследниками

from pygame.sprite import Sprite
from random import randint
from configs import E_PICKED
from time import time
from datatypes import OBJECTS_POOL, wpns
from . import real
import pygame
import utils


class TWObject(Sprite): # любой объект в игре так или иначе наследуется от этого класса

    def __init__(self, spawnpoint, *args, **kwargs):
        super().__init__()
        self.collideable = True # можно ли с объектом столкнуться
        self.pickable = False # можно ли объект подобрать
        self.updateable = False # требуется ли объекту постоянная рассылка обновлений своего состояния
        self._init_rect(*args, **kwargs)
        self.uid = kwargs.get('uid', None)
        if not self.uid: # если при создании не был передан uid, то генерируем его
            self.set_uid()
        self.rect = self.image.get_rect(center=spawnpoint) # для корректной отрисовки объект должен содержать поля self.rect и self.image
        self._postInit(*args, **kwargs) # чтоб можно было инициализировать свои поля и не переписывать конструктор
        self.orig_image = self.image # нужно для вращения объекта (при вращении одной и той же картинки теряется качество)
        OBJECTS_POOL.add_(self) # объект при создании автоматически добавляется в глобальный массив

            
    def set_uid(self, uid=None):
        if uid:
            self.uid = uid
            return
        while True:
            self.uid = randint(0, 65535) # генерируем до тех пор, пока не появится уникальное число
            if self.uid not in OBJECTS_POOL:
                break


    def __str__(self):
        return '%s %s' % (self._name, (self.rect.x, self.rect.y))


    def get_state(self): # получаем состояние объекта для его апдейта на всех клиентах (uid передаётся автоматически)
        return {
            'name': self._name,
            'coords': self.rect.center
        }
        
        
    @property
    def _name(self):
        return self.__class__.__name__
    
    
    def _init_rect(self, *args, **kwargs): # инициализация графония и фигуры для просчёта физики
        pass
    
    
    def _postInit(self, *args, **kwargs):
        pass
        
    
    def hide(self, h):
        if h:
            OBJECTS_POOL.remove_(self) # если прячем, то должны удостовериться, что объект ещё остался в памяти
        else:
            OBJECTS_POOL.add_(self)
        
        
    def _destroy(self): # при удалении подразумеваем, что ссылка на объект есть только в OBJECTS_POOL
        OBJECTS_POOL.remove_(self)
    
    
    def fx(self, surf):
        pass
    
    
class Pickable(TWObject):
    
    def __init__(self, spawnpoint, *args, **kwargs):
        super().__init__(spawnpoint, *args, **kwargs)
        self.pickable = True
        self.picked = False # для однократного сообщения серверу о взятии предмета
        self.collideable = False
    
    
    def picked_event(self, entity):
        if entity.client: # если являемся клиентом, то
            pygame.event.post(pygame.event.Event(E_PICKED, author=entity, target=self))
        else:
            if not self.picked:
                self.picked_by(entity)
                self.picked = True
    
    
    def picked_by(self, entity): # поднимаемое не может быть не поднято
        raise NotImplementedError



class Weapon(Pickable):

    def __init__(self, spawnpoint=None, *args, hidden=False, **kwargs):
        try:
            self.model = wpns[self._name] # получаем конфиги оружия
            self.image = self.model.img
        except KeyError:
            raise NotImplementedError(f'No model available for {self._name}')
        
        if 'owner' in kwargs:
            self.owner = kwargs['owner']
            super().__init__(self.owner.rect.center)
            self.pwned()
            if hidden:
                self.hide(True)
        else:
            super().__init__(spawnpoint, *args, **kwargs)
            self.owner = None
        self.last_shot = 0 # когда был произведён последний выстрел
        self.ammo = 20
        
        
    def picked_by(self, entity): # игрок подобрал оружие
        self.pwned()
        entity.weaponize(self)
        self.owner = entity

        
    def pwned(self):
        self.collideable = False
        self.pickable = False
        

    def update(self):
        if self.owner:
            # поворачиваем пушку вслед за направлением взгляда игрока
            degr = utils.u_degrees(utils.angleTo(self.owner.dir, self.rect.center)) if self.model.rot is None else self.model.rot
            self.image = pygame.transform.rotate(self.orig_image, degr)
            self.image = pygame.transform.flip(self.image, True, True)
            #if 90 <= degr <= 270:
            #    self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect(center=self.owner.rect.center) # оружие всегда торчит из центра игрока
        
        
    def shoot(self, proj_uid=None):
        if self.model.rate < (time() - self.last_shot):
            self.last_shot = time()
            return self._shooter(proj_uid)
            
        
    def _shooter(self, proj_uid=None):
        if self.ammo > 0:
            self.ammo -= 1
            return real.Projectile(self.owner.rect.center, model=self.model, owner=self.owner, uid=proj_uid).uid
    

