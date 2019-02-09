from pygame.sprite import OrderedUpdates
from threading import Lock
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

class TWOrderedUpdates(OrderedUpdates):
    
    def __init__(self):
        self.__uids = {}
        super().__init__()

    def add_(self, uid, sprite):
        with lock:
            self.__uids[uid] = sprite
            OrderedUpdates.add(self, sprite)

    def remove_(self, obj): # может прийти и uid, и TWobject
        with lock:
            if type(obj) == int:
                OrderedUpdates.remove(self, self.__uids[obj])
                del self.__uids[obj]
            else:
                OrderedUpdates.remove(self, obj)
                del self.__uids[obj.uid]

    def __getitem__(self, uid):
        return self.__uids.get(uid, None)
        

OBJECTS_POOL = TWOrderedUpdates()
        
def get_objects_pool():
    return OBJECTS_POOL

    
