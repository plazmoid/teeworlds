from pygame.sprite import Sprite
from random import randint
from configs import PLAYER_SIZE, JUMP_SPEED, GRAVITY, FRICTION, SPEED
import pygame
import utils

OBJECTS_POOL = utils.get_objects_pool()

class TWObject(Sprite):

    def __init__(self, sizes, uid=None):
        super().__init__()
        self.sizes = sizes
        self.collideable = True
        self.pickable = False
        self.is_player = False
        self._postInit()
        self.rect = pygame.Rect(*self.sizes)
        while True:
            if uid:
                self.uid = uid
                break
            self.uid = randint(0, 65535)
            if self.uid not in OBJECTS_POOL:
                break
        OBJECTS_POOL.add_(self.uid, self)

    def update(self):
        raise NotImplementedError

    def __str__(self):
        return '%s(%s)' % (self.__class__, self.sizes[:2])

    def getXY(self):
        return (self.rect.x, self.rect.y)
        
    def modifier(self, obj):
        pass
    
    def _postInit(self):
        pass


class Item(TWObject):
    
    def __init__(self, owner, size):
        super().__init__(list(owner.rect.center) + size)
        self.collideable = False
        
    
class GrapplingHook(TWObject):
    
    def __init__(self, owner):
        super().__init__((owner.rect.center))
        self.size = [40, 20]
        self.owner = owner
        self.image = pygame.image.load("img/rope.png")
        
    def update(self):
        self.rect.center = self.owner.rect.center
        
    def shoot(self):
        pass
    

class Player(TWObject):
    
    def __init__(self, spawnpoint, uid=None):
        super().__init__(spawnpoint+PLAYER_SIZE, uid=uid)
        
    def _postInit(self):
        self.image = pygame.image.load("img/gg.png")
        self.xvel = 0
        self.yvel = 0
        self.dir = 0
        self.keydir = [0,0]
        self.onGround = False
        self.collideable = False
        self.is_player = True
        #self.rope = Rope(self)        

    def update(self):
        if self.keydir[0] != 0: 
            self.xvel = self.keydir[0]*SPEED
        if self.keydir[1] == -1 and self.onGround:
            self.yvel -= JUMP_SPEED
            self.onGround = False
        
        self.rect.x += self.xvel
        self.rect.y += self.yvel
        self.onGround = False

        for obj in OBJECTS_POOL:
            if self != obj and pygame.sprite.collide_rect(self, obj):
                if obj.collideable:
                    self.onGround, self.xvel, self.yvel = self.collide(obj)
                    obj.modifier(self)
                if obj.pickable:
                    obj.picked(self)
        
        if not self.onGround:
            self.yvel += GRAVITY
        
        if abs(self.xvel) <= FRICTION:
            self.xvel = 0
        else:
            if self.xvel > 0:
                self.xvel -= FRICTION
            elif self.xvel < 0:
                self.xvel += FRICTION

    def collide(self, block):
        axis_rot = 45
        rot_coef = -3
        rot_offset_vert = axis_rot + rot_coef
        rot_offset_hrz = axis_rot - rot_coef
        f_up = 90
        f_left = 180
        f_down = 270
        entrSide = utils.u_degrees(utils.angleTo(block.rect.center, self.rect.center))
        if (f_up-rot_offset_vert) <= entrSide < (f_up+rot_offset_vert): #сверху
            self.rect.bottom = block.rect.top+1
            return (True, self.xvel, 0)
        elif (f_left-rot_offset_hrz) <= entrSide < (f_left+rot_offset_hrz): #слева
            self.rect.right = block.rect.left
            return (False, 0, self.yvel)
        elif (f_down-rot_offset_vert) <= entrSide < (f_down+rot_offset_vert): #снизу
            self.rect.top = block.rect.bottom
            if self.yvel < 0:
                return (False, self.xvel, 0)
            return (False, self.xvel, self.yvel)
        elif (360-rot_offset_hrz) <= entrSide or entrSide < rot_offset_hrz: #справа
            self.rect.left = block.rect.right
            return (False, 0, self.yvel)

###################################just becoz
    def moveAfterMouse(self, mouse_pos):
        self.angle = utils.angleTo(self.rect.center, mouse_pos)
        self.xvel, self.yvel = utils.toRectCoords(10, self.angle)

    def lookOnMouse(self, m_pos):
        self.dir = -1 if self.rect.centerx > m_pos[0] else 1



