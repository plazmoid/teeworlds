from pygame.sprite import Sprite
import pygame
import utils


PLATFORM_SIZE = 30
OBJECTS_POOL = pygame.sprite.OrderedUpdates()
PLAYER_SIZE = [20,20]
SPEED = 4
JUMP_SPEED = 7
GRAVITY = 0.3
FRICTION = GRAVITY*1.5


class TWObject(Sprite):

    def __init__(self, sizes):
        super().__init__()
        self.sizes = sizes
        self.collideable = True
        self.rect = pygame.Rect(*sizes)
        OBJECTS_POOL.add(self)

    def update(self):
        raise NotImplementedError

    def __str__(self):
        return '%s(%s)' % (self.__class__, self.sizes[:2])
    
    def getXY(self):
        return (self.rect.x, self.rect.y)
        
    def modifier(self, obj):
        pass


class DefaultBlock(TWObject):
    
    def __init__(self, point, size=[PLATFORM_SIZE]*2):
        super().__init__(point+size, )
        self.image = pygame.Surface(size)
        self.image.fill(pygame.Color('#ff6262'))

    def update(self):
        pass
    
    
class JumperBlock(DefaultBlock):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image.fill(pygame.Color('#5faa0a'))
        
    def modifier(self, obj):
        obj.yvel -= 10
    

class Item(TWObject):
    
    def __init__(self, owner, size):
        super().__init__(list(owner.rect.center) + size)
        self.collideable = False
        
    
class GrapplingHook(TWObject):
    
    def __init__(self, owner):
        self.size = [40, 20]
        self.owner = owner
        self.image = pygame.image.load("img/rope.png")
        
    def update(self):
        self.rect.center = self.owner.rect.center
        
    def shoot(self):
        pass
    

class Player(TWObject):
    
    def __init__(self, spawnpoint):
        super().__init__(spawnpoint+PLAYER_SIZE)
        self.image = pygame.image.load("img/gg.png")
        self.xvel = 0
        self.yvel = 0
        self.keydir = [0,0]
        self.dir = 0
        self.onGround = False
        self.collideable = False
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
            if obj.collideable and self != obj and pygame.sprite.collide_rect(self, obj):
                self.onGround, self.xvel, self.yvel = self.collide(obj)
                obj.modifier(self)
        
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

