from objects import TWObject
from configs import PLATFORM_SIZE
from world import GameEngine
import pygame
import utils


class DefaultBlock(TWObject):
    
    def __init__(self, point, size=[PLATFORM_SIZE]*2):
        super().__init__(point+size, )

    def update(self):
        pass
    
    def _postInit(self):
        self.image = pygame.Surface(self.sizes[2:])
        self.image.fill(pygame.Color('#ff6262'))
        
    
class JumperBlock(DefaultBlock):
    
    def _postInit(self):
        self.image = pygame.Surface(self.sizes[2:])
        self.image.fill(pygame.Color('#5faa0a'))
        
    def modifier(self, obj):
        obj.yvel -= 10
    
    
class Pickable(TWObject):
    
    def __init__(self, point, uid=None):
        super().__init__(point + [PLATFORM_SIZE-10]*2)
        self.pickable = True
    
    def picked_by(self, entity):
        raise NotImplementedError
    

class Heart(Pickable):
    
    def _postInit(self):
        self.image = pygame.Surface(self.sizes[2:])
        self.image.fill(pygame.Color('#ff33b8'))

    def picked_by(self, entity):
        GameEngine.logger.info(f'{entity} picked a heart')
        utils.get_objects_pool().remove_(self)
    
    