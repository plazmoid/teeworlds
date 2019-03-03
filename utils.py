from pygame.sprite import OrderedUpdates
from threading import Lock
import math


def angleTo(p_from, p_to): #два кортежа координат
    return math.atan2(p_from[1] - p_to[1], p_to[0] - p_from[0])

def u_degrees(rad):
    return int(math.degrees(rad) % 360)

def distTo(p_from, p_to):
    return math.sqrt((p_to[0] - p_from[0])**2 + (p_from[1] - p_to[1])**2)


lock = Lock()

class TWOrderedUpdates(OrderedUpdates): # массив спрайтов, в тоже время дающий доступ к любому TWObject'у по его uid'у
    
    def __init__(self):
        self.__uids = {}
        super().__init__()


    def add_(self, uid, sprite):
        with lock:
            self.__uids[uid] = sprite # дублирующий словарь {TWObject.uid: TWObject}
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
    
    
    def __repr__(self):
        return str(self.__uids)
    
    
    def custom_draw(self, surface): # каждому объекту позволено оставить свой след на холсте
        for sprite in self:
            sprite.drawings(surface)
        

OBJECTS_POOL = TWOrderedUpdates()
        
def get_objects_pool():
    return OBJECTS_POOL # на всякий случай


    
    
    