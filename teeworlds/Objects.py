from pygame.sprite import Sprite as Sprite
import utils
import pygame

PLATFORM_SIZE = 30

class UpdSpriteGroup(pygame.sprite.Group):
    
    def update(self):
        for itm in self:
            if type(itm) != Block:
                itm.update()

    def draw_n_update(self, surface):
        self.update()
        super().draw(surface)

ALL_OBJECTS = UpdSpriteGroup()

class GameObject(Sprite):

    def __init__(self, sizes, collideable=True):
        super().__init__()
        self.sizes = sizes
        self.collideable = collideable
        self.rect = pygame.Rect(*sizes)
        ALL_OBJECTS.add(self)

    def update(self, coords=None):
        if not coords:
            return
        self.rect.center = coords

    def __repr__(self):
        return '%s(%s)' % (self.__class__, self.sizes[:2])


class Block(GameObject):
    
    axis_rot = 45
    rot_coef = -3
    rot_offset_vert = axis_rot + rot_coef
    rot_offset_hrz = axis_rot - rot_coef
    f_up = 90
    f_left = 180
    f_down = 270
    
    def __init__(self, point, size=[PLATFORM_SIZE]*2):
        super().__init__(point+size)
        self.image = pygame.Surface(size)
        self.image.fill(pygame.Color('#ff6262'))

    def collide(self, entity): #что-то сталкивается с кубиком
        self.entrSide = utils.u_degrees(utils.angleTo(self.rect.center, entity.rect.center))
        if (self.f_up-self.rot_offset_vert) <= self.entrSide < (self.f_up+self.rot_offset_vert): #сверху
            entity.rect.bottom = self.rect.top+1
            return (True, entity.xvel, 0)
        elif (self.f_left-self.rot_offset_hrz) <= self.entrSide < (self.f_left+self.rot_offset_hrz): #слева
            entity.rect.right = self.rect.left
            return (False, 0, entity.yvel+0.1)
        elif (self.f_down-self.rot_offset_vert) <= self.entrSide < (self.f_down+self.rot_offset_vert): #снизу
            entity.rect.top = self.rect.bottom
            if entity.yvel < 0:
                return (False, entity.xvel, 0)
            return (False, entity.xvel, entity.yvel)
        elif (360-self.rot_offset_hrz) <= self.entrSide or self.entrSide < self.rot_offset_hrz: #справа
            entity.rect.left = self.rect.right
            return (False, 0, entity.yvel+0.1 if entity.yvel < 0 else entity.yvel)
        raise RuntimeError('Bad collision')


class JumperBlock(Block):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image.fill(pygame.Color('#5faa0a'))
        
    def collide(self, entity):
        self.result = list(super().collide(entity))
        self.result[2] = -(7*1.3)
        return tuple(self.result)