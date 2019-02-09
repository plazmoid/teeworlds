from pygame.sprite import OrderedUpdates
from threading import Lock
import pygame
import math
import cmath


def angleTo(p_from, p_to): #два кортежа координат
    return math.atan2(p_from[1] - p_to[1], p_to[0] - p_from[0])

def u_degrees(rad):
    return int(math.degrees(rad) % 360)

def toRectCoords(r, phi):
    res = cmath.rect(r, phi)
    return (round(res.real), -round(res.imag))

def distTo(p_from, p_to):
    return math.sqrt((p_to[0] - p_from[0])**2 + (p_from[1] - p_to[1])**2)


lock = Lock()

class TWOrderedUpdates(OrderedUpdates): # массив спрайтов, в тоже время дающий доступ к любому TWObject'у по его uid'у
    
    def __init__(self):
        self.__uids = {}
        super().__init__()


    def add_(self, uid, sprite):
        with lock:
            self.__uids[uid] = sprite # внутри просто дублирующий словарь {TWObject().uid: TWObject()}
            self.add(sprite)


    def remove_(self, obj): # может прийти и uid, и TWobject
        if type(obj) == int:
            obj = self.__uids.get(obj, None)
        if obj in self:
            with lock:
                self.remove(obj)
                del self.__uids[obj.uid]


    def __getitem__(self, uid): #из массива можно выбирать объекты по uid'e, как из словаря
        return self.__uids.get(uid, None)
    
    
    def custom_draw(self, surface): # каждому объекту позволено оставить свой след на холсте
        for sprite in self:
            sprite.drawings(surface)
        

OBJECTS_POOL = TWOrderedUpdates()
        
def get_objects_pool():
    return OBJECTS_POOL # на всякий случай


class PicContainer: # удобный резчик картиночек
        
    cached_Pic = None # последний загруженный экземпляр класса Pic
    
    def __init__(self):
        self.pics = {}
    
    class Pic:
        
        def __init__(self, name, path, dims):
            self.name = name
            self.path = path
            self.dims = dims # dimensions (x, y, w, h)
            self.size = self.dims[2:]
            self.rect = pygame.Rect(*self.dims)
            self.raw_pic = None # картинка с диска
            self.pic = None # вырезанная из картинки пиктограмма
            
        def load(self):
            if not PicContainer.cached_Pic or PicContainer.cached_Pic.path != self.path: # если была загружена другая картинка, то загружаем новую
                self.raw_pic = pygame.image.load(self.path)
                PicContainer.cached_Pic = self # и сохраняем в кэш
            else:
                self.raw_pic = PicContainer.cached_Pic.raw_pic
            self.pic = self.raw_pic.subsurface(self.rect) # вырезаем из картинки нужную область
            return self
        
        def draw_ready(self):
            return self.size, self.pic
                
        
    def add(self, picname, path, dims):
        self.pics[picname] = self.Pic(picname, path, dims)

    
    def get(self, picname):
        return self.pics[picname].load()
    
    
# удобно же, ну
piccontainer = PicContainer()
piccontainer.add('heart_full', 'img/game.png', (670, 0, 65, 65))
piccontainer.add('heart_empty', 'img/game.png', (735, 0, 65, 65))
piccontainer.add('heart_loot', 'img/game.png', (320, 70, 60, 50))
piccontainer.add('hook', 'img/game.png', (60, 0, 110, 30))
piccontainer.add('hammer', 'img/game.png', (65, 40, 125, 80))
piccontainer.add('aim_default', 'img/game.png', (0, 0, 65, 65))
piccontainer.add('aim_gun', 'img/game.png', (0, 130, 65, 65))
    
    
    
    