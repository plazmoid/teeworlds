# Здесь собраны все реальные объекты, которые есть в игре. Их можно заспавнить и уничтожить.

from objects import abstract
from configs import JUMP_SPEED, GRAVITY, FRICTION, SPEED, PLATFORM_SIZE, MAX_LIFES, E_KILLED
from pygame import math as pmath
from datatypes import OBJECTS_POOL, pics
import pygame
import utils



class DefaultBlock(abstract.TWObject): # блок уровня
    
    def _init_rect(self, *args, **kwargs):
        self.image = pygame.Surface((PLATFORM_SIZE, PLATFORM_SIZE))
        self.image.fill(pygame.Color('#905c2f'))


class Player(abstract.TWObject): # игрок тоже наследуется от TWObject, что позволяет ему иметь свой uid и упрощать клиент-серверное общение

    def _init_rect(self, *args, **kwargs):
        self.image = pics['tee']
        
        
    def _postInit(self, client=False, *args, **kwargs):
        self.updateable = True # любой игрок должен обновляться постоянно
        self.client = client # является ли игрок нами
        self.active = None # текущее оружие в руках
        self.rect.center = pmath.Vector2(self.rect.center)
        self.velocity = pmath.Vector2(0, 0) # скорость представляем в виде вектора для удобства
        self.keydir = pmath.Vector2(0, 0) # как и нажатые клавиши
        self.lifes = 10 
        self.dir = (0, 0)
        self.onGround = False
        self.collideable = False # игроки не сталкиваются
        self.count = 0 # очки
        self.hook = GrapplingHook(owner=self)
        self.weapons = dict(map(lambda x: (x.__name__, x(owner=self, hidden=True)), # здесь валяется всё оружие игрока
                [Hammer, Pistol, Shotgun, GrenadeLauncher, Ninja, Laser]))
        self.wpnswitcher = {getattr(pygame, 'K_%s' % (i+1)):v for i, v in enumerate(self.weapons)}
        self.switch_weapon('Hammer')
        self.respawn()
        
    
    def respawn(self):
        self.velocity = pmath.Vector2(0, 0)
        self.lifes = 10
        self.armor = 0
        for wpn in self.weapons.values():
            wpn.ammo = 15
    
    
    def switch_weapon(self, key):
        try:
            if type(key) == str:
                wname = key
            else:
                wname = self.wpnswitcher[key]
            next_wpn = self.weapons[wname]
        except KeyError:
            return
        if self.active:
            self.active.hide(True)
        self.active = next_wpn
        self.active.hide(False)


    def get_state(self):
        state = super().get_state()
        state['vel'] = self.velocity
        state['dir'] = self.dir
        state['lifes'] = self.lifes
        state['wpn'] = self.active._name
        state['count'] = self.count
        return state
        

    def update(self): # физика, физика
        if self.client:
            self.dir = pygame.mouse.get_pos()
        if self.keydir.x != 0: 
            self.velocity.x = self.keydir.x*SPEED
        if self.keydir.y == -1 and self.onGround:
            self.velocity.y -= JUMP_SPEED
            
        grapnel = self.hook.grapnel # физика хука
        if grapnel and grapnel.hooked:
            #print(grapnel.hook_max_dist - grapnel.dist)
            delta = grapnel.hook_max_dist - grapnel.dist
            if delta < 20:
                vec_player_grapnel = pmath.Vector2(grapnel.rect.center) - self.rect.center
                try:
                    vec_player_grapnel = vec_player_grapnel.normalize() * self.velocity.length()
                    #print(f'{vec_player_grapnel}, {self.velocity.normalize()}')
                    self.velocity = vec_player_grapnel
                except ValueError: # если вектор вдруг нулевой
                    pass
        
        self.onGround = False
            

        for collided in pygame.sprite.spritecollide(self, OBJECTS_POOL, False): # проверки на столкновения с объектами на уровне
            if collided.collideable:
                self.collide(collided)
            if collided.pickable:
                collided.picked_event(self)
        
        if not self.onGround:
            self.velocity.y += GRAVITY # гравитацией снижаем высоту прыга
            
        self.rect.center += self.velocity
        
        if abs(self.velocity.x) <= FRICTION: # а трением не даём скользить из стены в стену
            self.velocity.x = 0
        else:
            if self.velocity.x > 0:
                self.velocity.x -= FRICTION
            elif self.velocity.x < 0:
                self.velocity.x += FRICTION
                
        

    def collide(self, block):            
        axis_rot = 45
        rot_coef = -2
        rot_offset_vert = axis_rot + rot_coef
        rot_offset_hrz = axis_rot - rot_coef
        f_up = 90
        f_left = 180
        f_down = 270
        entrSide = utils.u_degrees(utils.angleTo(block.rect.center, self.rect.center))
        if (f_up-rot_offset_vert) <= entrSide < (f_up+rot_offset_vert): #сверху
            self.rect.bottom = block.rect.top + 1
            self.onGround = True
            if self.velocity.y > 0:
                self.velocity.y = 0
        elif (f_left-rot_offset_hrz) <= entrSide < (f_left+rot_offset_hrz): #слева
            self.rect.right = block.rect.left - 1
            self.velocity.x = 0
        elif (f_down-rot_offset_vert) <= entrSide < (f_down+rot_offset_vert): #снизу
            self.rect.top = block.rect.bottom
            if self.velocity.y < 0:
                self.velocity.y = 0
        elif (360-rot_offset_hrz) <= entrSide or entrSide < rot_offset_hrz: #справа
            self.rect.left = block.rect.right + 1
            self.velocity.x = 0
            
            
    #def weaponize(self, weapon):
    #    if self.active == None:
    #        self.active = weapon
    #    self.weapons.append(weapon)
        
        
    def hit(self, obj):
        if not self.client:
            self.lifes -= obj.model.dmg
        if self.lifes <= 0:
            pygame.event.post(pygame.event.Event(E_KILLED, author=obj.owner, target=self))
            
            
    def _destroy(self):
        self.active._destroy()
        super()._destroy()


class Heart(abstract.Pickable): # подбираемое сердечко, восстанавливает одну хпшчку
    
    def _init_rect(self, *args, **kwargs):
        self.image = pics.get('heart_loot')
        self.updateable = True        
        

    def picked_by(self, entity):
        if entity.lifes <= MAX_LIFES:
            entity.lifes += 1
        
        
    def update(self):
        pass


class Projectile(abstract.TWObject):
    
    def _init_rect(self, *args, **kwargs):
        self.model = kwargs['model']
        self.image = self.model.proj
        
        
    def _postInit(self, *args, **kwargs):
        self.owner = kwargs['owner']
        self.collideable = False
        self.updateable = True
        self.velocity = pmath.Vector2(0, 0)
        angle = utils.u_degrees(-utils.angleTo(self.rect.center, self.owner.dir))
        self.image = pygame.transform.rotate(self.image, angle)
        self.image = pygame.transform.flip(self.image, False, True)
        self.velocity.from_polar((self.model.speed, angle))
        self.delta_y = GRAVITY/(self.model.flatness*2)
    
        
    def update(self):
        self.velocity.y += self.delta_y
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        
        target = pygame.sprite.spritecollideany(self, OBJECTS_POOL)
        if not target:
            return
        is_player = (target._name == 'Player' and target != self.owner)
        if target.collideable or is_player:
            if self.model.splash_r > 0:
                for victim in OBJECTS_POOL:
                    if victim._name == 'Player' and utils.distTo(victim.rect.center, self.rect.center) <= self.model.splash_r:
                        victim.hit(self)
            else:
                if is_player:
                    target.hit(self)
            self._destroy()

    
    
class Grapnel(Projectile): # крюк как снаряд
        
    def _postInit(self, *args, **kwargs):
        Projectile._postInit(self, *args, **kwargs)
        self.hooked = False
        self.chain = pics['GrapplingHook_chain']
        self.chain_orig = self.chain
        

    def update(self):
        self.rect.center += self.velocity
        self.dist = utils.distTo(self.owner.rect.center, self.rect.center)
        
        if self.dist > 300: # хук имеет максимальную дистанцию
            self._destroy()
        
        if not self.hooked:
            target = pygame.sprite.spritecollideany(self, OBJECTS_POOL) # ищем объект, за который можно зацепиться
            if target and target.collideable:
                self.velocity.x = 0
                self.velocity.y = 0
                self.hooked = True
                self.hook_max_dist = self.dist
        else:
            if self.dist > self.hook_max_dist: # если растянулись сильнее дозволенного, то хук рвётся
                self.hooked = False
                self.owner.hook.release()
        self.angle = utils.angleTo(self.rect.center, self.owner.rect.center)
        degr = utils.u_degrees(self.angle)
        self.image = pygame.transform.rotate(self.orig_image, degr)
        #self.image = pygame.transform.flip(self.image, True, True)
        #self.rect = self.image.get_rect(center=self.rect.center)
    
        
    def fx(self, surf): # рисуем звенья цепи
        link_width = self.chain.get_rect().width - 3
        link_pos = pmath.Vector2(self.rect.center)
        link_delta = pmath.Vector2(self.rect.center)
        angle = utils.u_degrees(-self.angle)
        link_delta.from_polar((link_width, angle))
        links_cnt = int(self.dist // link_width)
        self.chain = pygame.transform.rotate(self.chain_orig, angle)
        self.chain = pygame.transform.flip(self.chain, False, True)
        for _ in range(links_cnt):
            link_pos += link_delta
            surf.blit(self.chain, link_pos)                     


class GrapplingHook(abstract.Weapon): # крюк как оружие

    def _postInit(self, *args, **kwargs):
        abstract.Weapon._postInit(self, *args, **kwargs)
        self.grapnel = None
        
    
    def _shooter(self, proj_uid=None):
        self.grapnel = Grapnel(self.owner.rect.center, model=self.model, owner=self.owner, uid=proj_uid)
        return self.grapnel.uid
        
        
    def release(self):
        if self.grapnel:
            self.grapnel._destroy()
            self.grapnel = None
        return 'release'


class Hammer(abstract.Weapon):

    def _shooter(self, proj_uid=None):
        for obj in OBJECTS_POOL:
            if self != obj and pygame.sprite.collide_rect(self, obj):
                if obj._name == 'Player' and obj != self.owner:
                    obj.hit(self)            


class Pistol(abstract.Weapon): pass


class Shotgun(abstract.Weapon): pass


class GrenadeLauncher(abstract.Weapon): pass


class Ninja(abstract.Weapon):
    
    def _shooter(self, proj_uid=None):
        for obj in OBJECTS_POOL:
            if self != obj and pygame.sprite.collide_rect(self, obj):
                if obj._name == 'Player' and obj != self.owner:
                    obj.hit(self)            

        
class Laser(abstract.Weapon): pass
        
        
        
