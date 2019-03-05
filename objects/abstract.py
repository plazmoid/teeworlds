# Тут свалены абстракции, т.е. предметы, которые создавать бессмысленно, но их каркас используется наследниками

from pygame.sprite import Sprite
from pygame import math as pmath
from random import randint
from configs import E_PICKED, GRAVITY
from time import time
import pygame
import utils
import datatypes

OBJECTS_POOL = datatypes.get_objects_pool()
wpns = datatypes.wpns

class TWObject(Sprite): # любой объект в игре так или иначе наследуется от этого класса

    def __init__(self, spawnpoint, *args, **kwargs):
        super().__init__()
        self.collideable = True # можно ли с объектом столкнуться
        self.pickable = False # можно ли объект подобрать
        self._init_rect(*args, **kwargs)
        if 'uid' not in kwargs: # если при создании не был передан uid, то генерируем его
            self.set_uid()
        else:
            self.uid = kwargs['uid']
        self.rect = self.image.get_rect(center=spawnpoint) # для корректной отрисовки объект должен содержать поля self.rect и self.image
        self._postInit(*args, **kwargs) # чтоб можно было инициализировать свои полей и не переписывать конструктор
        self.orig_image = self.image
        OBJECTS_POOL.add_(self.uid, self) # объект при создании автоматически добавляется в глобальный массив

            
    def set_uid(self, uid=None):
        if uid:
            self.uid = uid
            return
        while True:
            self.uid = randint(0, 65535) # генерируем до тех пор, пока не появится уникальное число
            if self.uid not in OBJECTS_POOL:
                break


    def update(self):
        raise NotImplementedError # каждый объект должен как-нибудь обновляться

    def __str__(self):
        return '%s %s' % (self._name(), (self.rect.x, self.rect.y))

    def get_state(self): # получаем состояние объекта для его апдейта на всех клиентах (uid передаётся автоматически)
        return {
            'name': self._name(),
            'coords': self.rect.center
        }
        
    def _name(self):
        return self.__class__.__name__
    
    def _init_rect(self, *args, **kwargs):
        pass
    
    def _postInit(self, *args, **kwargs):
        pass
    
    
    def drawings(self, surface): # дорисосываем что-нибудь поверх всего игрового поля
        pass
        
    
    def hide(self, h, obj=None):
        if h:
            OBJECTS_POOL.remove_(self) # если прячем, то надеемся, что объект ещё остался в памяти
        else:
            OBJECTS_POOL.add_(obj.uid, obj)
        
        
    def _destroy(self):
        OBJECTS_POOL.remove_(self)
        
        
    def modifier(self, obj): # для джамппада, скорей всего в мусор
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

    def __init__(self, spawnpoint=None, *args, **kwargs):
        try:
            name = self.__class__.__name__
            self.model = wpns[name] # получаем конфиги оружия
            self.image = self.model.img
        except KeyError:
            raise NotImplementedError(f'No model available for {name}')
        
        if 'owner' in kwargs:
            self.owner = kwargs['owner']
            super().__init__(self.owner.rect.center)
            self.pwned()
        else:
            super().__init__(spawnpoint, *args, **kwargs)
            self.owner = None
        self.last_shot = 0
        self.ammo = 10
        
        
    def picked_by(self, entity):
        self.pwned()
        entity.weaponize(self)
        self.owner = entity
        
        
    def pwned(self):
        self.collideable = False
        self.pickable = False
        

    def update(self):
        if self.owner:
            # поворачиваем пушку вслед за направлением взгляда игрока
            degr = utils.u_degrees(utils.angleTo(self.owner.dir, self.rect.center))
            self.image = pygame.transform.rotate(self.orig_image, degr)
            self.image = pygame.transform.flip(self.image, True, True)
            #if 90 <= degr <= 270:
            #    self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(center=self.owner.rect.center) # оружие всегда торчит из центра игрока
        
        
    def shoot(self):
        if self.model.rate < (time() - self.last_shot): 
            Projectile(self.owner.rect.center, model=self.model)
            self.last_shot = time()
    

class Projectile(TWObject):
    
    def _init_rect(self, *args, **kwargs):
        self.model = kwargs['model']
        self.image = self.model.proj
        
        
    def _postInit(self, *args, **kwargs):
        self.collideable = False
        self.velocity = pmath.Vector2(0, 0)
        angle = utils.u_degrees(-utils.angleTo(self.rect.center, pygame.mouse.get_pos()))
        self.image = pygame.transform.rotate(self.image, angle)
        self.image = pygame.transform.flip(self.image, False, True)
        self.velocity.from_polar((self.model.speed, angle))
    
        
    def update(self):
        self.velocity.y += GRAVITY/self.model.flatness
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        for obj in OBJECTS_POOL: # проверки на столкновения с объектами на уровне
            if self != obj and pygame.sprite.collide_rect(self, obj):
                if obj._name() == 'Player': 
                    obj.hit(self)
                if obj.collideable:
                    self.kaboom()
                    
                    
    def kaboom(self):
        self._destroy()

