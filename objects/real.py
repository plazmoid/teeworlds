# Здесь собраны все реальные объекты, которые есть в игре. Их можно заспавнить и уничтожить.

from objects import abstract
from configs import PLAYER_SIZE, JUMP_SPEED, GRAVITY, FRICTION, SPEED, PLATFORM_SIZE, E_PICKED, E_REPOS, MAX_LIFES
from pygame import math as pmath
import pygame
import utils
import datatypes


OBJECTS_POOL = utils.get_objects_pool()
picloader = datatypes.piccontainer


class DefaultBlock(abstract.TWObject): # блок уровня

    def update(self):
        pass
    
    def _postInit(self):
        self.image = pygame.Surface((PLATFORM_SIZE, PLATFORM_SIZE))
        self.image.fill(pygame.Color('#905c2f'))
        
    
class JumperBlock(DefaultBlock): # зачем
    
    def _postInit(self):
        super()._postInit()
        self.image.fill(pygame.Color('#5faa0a'))
        
    def modifier(self, obj):
        obj.velocity.y -= 10 
    
    

class Player(abstract.TWObject): # даже игрок наследуется от TWObject, что позволяет ему иметь свой uid и упрощать клиент-серверное общение
        
    def __init__(self, *args, client=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client # является ли игрок нами
        
        
    def _postInit(self):
        self.image = pygame.image.load("img/gg.png")
        self.velocity = pmath.Vector2(0, 0) # скорость представляем в виде вектора для удобства
        self.keydir = pmath.Vector2(0, 0) # как и нажатые клавиши
        self.dir = (0, 0)
        self.onGround = False
        self.collideable = False # игроки не сталкиваются
        self.lifes = 2
        self.weapons = {} # здесь валяется всё оружие игрока


    def get_state(self):
        state = super().get_state()
        state['dir'] = self.dir
        state['lifes'] = self.lifes
        return state
        

    def update(self): # физика, физика
        if self.client:
            self.dir = pygame.mouse.get_pos()
        self.old_rect = self.rect.center
        if self.keydir.x != 0: 
            self.velocity.x = self.keydir.x*SPEED
        if self.keydir.y == -1 and self.onGround:
            self.velocity.y -= JUMP_SPEED
        
        self.onGround = False
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        for obj in OBJECTS_POOL: # проверки на столкновения с объектами на уровне
            if self != obj and pygame.sprite.collide_rect(self, obj):
                if obj.collideable:
                    self.collide(obj)
                    obj.modifier(self)
                if obj.pickable:
                    obj.picked_by(self)
        
        if not self.onGround:
            self.velocity.y += GRAVITY # гравитацией снижаем высоту прыга
        
        if abs(self.velocity.x) <= FRICTION: # а трением не даём скользить из стены в стену
            self.velocity.x = 0
        else:
            if self.velocity.x > 0:
                self.velocity.x -= FRICTION
            elif self.velocity.x < 0:
                self.velocity.x += FRICTION
        #if self.rect.center != self.old_rect:
        #    pygame.event.post(pygame.event.Event(E_REPOS))    
                

    def collide(self, block):
        axis_rot = 45
        rot_coef = -1
        rot_offset_vert = axis_rot + rot_coef
        rot_offset_hrz = axis_rot - rot_coef
        f_up = 90
        f_left = 180
        f_down = 270
        entrSide = utils.u_degrees(utils.angleTo(block.rect.center, self.rect.center)) # матааааааан, который понимает, столкнулись ли мы
        if (f_up-rot_offset_vert) <= entrSide < (f_up+rot_offset_vert): #сверху
            self.rect.bottom = block.rect.top+1
            self.onGround = True
            self.velocity.y = 0
        elif (f_left-rot_offset_hrz) <= entrSide < (f_left+rot_offset_hrz): #слева
            self.rect.right = block.rect.left-1
            self.velocity.x = 0
        elif (f_down-rot_offset_vert) <= entrSide < (f_down+rot_offset_vert): #снизу
            self.rect.top = block.rect.bottom
            if self.velocity.y < 0:
                self.velocity.y = 0
        elif (360-rot_offset_hrz) <= entrSide or entrSide < rot_offset_hrz: #справа
            self.rect.left = block.rect.right+1
            self.velocity.x = 0
        
        
    def drawings(self, surface):
        if self.client:
#             myfont = pygame.font.SysFont('Sans Serif', 25)
#             txt = f'{self.dir}'
#             textsurface = myfont.render(txt, False, (0, 0, 0))
#             surface.blit(textsurface,(0,60))
            heart_full = picloader.get('heart_full').pic # рисуем шкалу здоровья
            heart_empty = picloader.get('heart_empty').pic
            h_draw_coeff = 70
            for h in range(MAX_LIFES):
                h_img = heart_full if h+1 <= self.lifes else heart_empty
                surface.blit(h_img, (h*h_draw_coeff, 5))
        
            
    def weaponize(self, weapon_name):
        self.weapons[weapon_name] = WPN_CATALOG[weapon_name](self) # вооружаем игрока чем-нибудь
        

###################################just becoz # пригодится для прицела
    def moveAfterMouse(self, mouse_pos):
        self.angle = utils.angleTo(self.rect.center, mouse_pos)

    def lookOnMouse(self, m_pos):
        self.dir = -1 if self.rect.centerx > m_pos[0] else 1


class Heart(abstract.Pickable): # подбираемое сердечко, восстанавливает одну хпшчку
    
    def _postInit(self):
        super()._postInit()
        self.image = picloader.get('heart_loot').pic
        

    def picked_by(self, entity):
        if entity.lifes <= MAX_LIFES:
            entity.lifes += 1
        pygame.event.post(pygame.event.Event(E_PICKED, author=entity, target=self))
        
    
class GrapplingHook(abstract.Weapon):
    
    def _postInit(self):
        self.image = picloader.get('hook').pic
        
        
    def shoot(self):
        pass


#class Hammer(abstract.Weapon):
    
    
WPN_CATALOG = {
    'hook': GrapplingHook
}

