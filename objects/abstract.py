from pygame.sprite import Sprite
from random import randint
from configs import PLATFORM_SIZE
import pygame
import utils

OBJECTS_POOL = utils.get_objects_pool()

class TWObject(Sprite):

    def __init__(self, sizes, uid=None):
        super().__init__()
        self.sizes = sizes
        self.collideable = True
        self.pickable = False
        
        while True:
            if uid:
                self.uid = uid
                break
            self.uid = randint(0, 65535)
            if self.uid not in OBJECTS_POOL:
                break
        self._postInit()
        self.rect = pygame.Rect(*self.sizes)
        OBJECTS_POOL.add_(self.uid, self)

    def update(self):
        raise NotImplementedError

    def __str__(self):
        return '%s(%s)' % (self.__class__, self.sizes[:2])

    def getXY(self):
        return (self.__class__.__name__, self.rect.x, self.rect.y)
        
    def modifier(self, obj):
        pass
    
    def _postInit(self):
        pass
    
    
class Pickable(TWObject):
    
    def __init__(self, point, uid=None):
        super().__init__(point + [PLATFORM_SIZE-10]*2, uid=uid)
        self.pickable = True
        self.collideable = False
    
    def picked_by(self, entity):
        raise NotImplementedError
    
    def update(self):
        pass


class Item(TWObject):
    
    def __init__(self, owner, size):
        super().__init__(list(owner.rect.center) + size)
        self.collideable = False

