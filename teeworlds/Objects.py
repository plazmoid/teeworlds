from pygame.sprite import Sprite
import pygame

PLATFORM_SIZE = 30
OBJECTS_POOL = pygame.sprite.OrderedUpdates()


class GameObject(Sprite):

    def __init__(self, sizes):
        super().__init__()
        self.sizes = sizes
        self.collideable = True
        self.updateable = True
        self.rect = pygame.Rect(*sizes)
        OBJECTS_POOL.add(self)

    def update(self):
        raise NotImplementedError

    def __str__(self):
        return '%s(%s)' % (self.__class__, self.sizes[:2])
    
    def getXY(self):
        return '%d|%d' % (self.rect.x, self.rect.y)


class Block(GameObject):
    
    def __init__(self, point, size=[PLATFORM_SIZE]*2):
        super().__init__(point+size, )
        self.image = pygame.Surface(size)
        self.image.fill(pygame.Color('#ff6262'))
        self.updateable = False

    def update(self):
        pass
    

class Item(GameObject):
    
    def __init__(self, owner, size):
        super().__init__(list(owner.rect.center) + size)
        self.collideable = False
    
class Rope(GameObject):
    
    def __init__(self, owner):
        self.size = [40, 20]
        self.owner = owner
        self.image = pygame.image.load("img/rope.png")
        
    def update(self):
        self.rect.center = self.owner.rect.center
        
    def shoot(self):
        pass