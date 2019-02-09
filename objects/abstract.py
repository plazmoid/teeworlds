# Тут свалены абстракции, т.е. предметы, которые создавать бессмысленно, но их каркас используется наследниками

from pygame.sprite import Sprite
from random import randint
from configs import PLATFORM_SIZE
import pygame
import utils

OBJECTS_POOL = utils.get_objects_pool()

class TWObject(Sprite): # любой объект в игре так или иначе наследуется от этого класса

    def __init__(self, sizes=[0,0,0,0], uid=None):
        super().__init__()
        self.uid = uid
        self.sizes = list(sizes)
        self.collideable = True # можно ли с объектом столкнуться
        self.pickable = False # можно ли объект подобрать
        self._postInit() # чтоб можно было инициализировать пару своих полей и не переписывать конструктор
        if not self.uid: # если при создании не был передан uid, то генерируем его
            self.set_uid()
        self.rect = pygame.Rect(*self.sizes) # для корректной отрисовки объект должен содержать поля self.rect и self.image
        OBJECTS_POOL.add_(self.uid, self) # объект при создании автоматически добавляется в глобальный массив
        
        
    def set_size(self, w, h):
        ls = len(self.sizes)
        if ls == 2:
            self.sizes.extend([w, h])
        elif ls == 4:
            self.sizes[2:] = [w, h]

            
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
        return '%s(%s)' % (self.__class__.__name__, (self.rect.x, self.rect.y))

    def getXY(self): # получаем координаты объекта для его апдейта на всех клиентах
        return (self.__class__.__name__, self.rect.x, self.rect.y)
        
    def modifier(self, obj): # для джамппада, скорей всего в мусор
        pass
    
    def _postInit(self):
        pass
    
    def drawings(self, surface): # дорисосываем что-нибудь поверх всего игрового поля
        pass
    
    
class Pickable(TWObject):
    
    def _postInit(self):
        self.set_size(PLATFORM_SIZE-10, PLATFORM_SIZE-10)
        self.pickable = True
        self.collideable = False
    
    def picked_by(self, entity): # поднимаемое не может быть не поднято
        raise NotImplementedError
    
    def update(self):
        pass


class Weapon(TWObject):
    
    def __init__(self, owner):
        super().__init__(owner.rect.center) 
        self.collideable = False
        self.owner = owner
        self.name = 'Noname weapon'
        
    def update(self):
        self.rect.center = self.owner.rect.center # оружие всегда торчит из центра игрока
        

