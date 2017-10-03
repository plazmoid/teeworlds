import pygame
import Objects, utils

PLAYER_SIZE = [20,20]
SPEED = 4
JUMP_SPEED = SPEED + 3
GRAVITY = 0.3
FRICTION = GRAVITY*1.5


class Alive(Objects.GameObject):
    
    def __init__(self, sizes):
        super().__init__(sizes)
        self.xvel = 0
        self.yvel = 0
        self.keydir = [0,0]
        self.dir = 0
        self.onGround = False

    def update(self):
        if self.keydir[0] != 0: self.xvel = self.keydir[0]*SPEED
        if self.keydir[1] == -1 and self.onGround:
            self.yvel = -JUMP_SPEED
            self.onGround = False

        self.rect.x += self.xvel
        self.rect.y += self.yvel
        self.onGround = False

        for block in Objects.ALL_OBJECTS:
            if block.collideable and self != block and pygame.sprite.collide_rect(self, block):
                self.onGround, self.xvel, self.yvel = block.collide(self)
        
        if not self.onGround:
            self.yvel += GRAVITY
            
        if abs(self.xvel) <= FRICTION:
            self.xvel = 0
        else:
            if self.xvel > 0:
                self.xvel -= FRICTION
            elif self.xvel < 0:
                self.xvel += FRICTION
                

class Player(Alive):

    def __init__(self, point):
        super().__init__(point+PLAYER_SIZE)
        self.image = pygame.image.load("img/gg.png")
        self.rope = Rope(self)

    def moveAfterMouse(self, m_pos):
        self.angle = utils.angleTo(self.rect.center, m_pos)
        self.xvel, self.yvel = utils.toRectCoords(10, self.angle)

    def lookOnMouse(self, m_pos):
        self.dir = -1 if self.rect.centerx > m_pos[0] else 1


class Rope(Objects.GameObject):
    
    def __init__(self, owner):
        self.size = [40, 20]
        self.owner = owner
        super().__init__(list(owner.rect.center) + self.size, collideable=False)
        self.image = pygame.image.load("img/rope.png")
        
    def update(self):
        super().update(coords=self.owner.rect.center)
        
    def shoot(self):
        pass