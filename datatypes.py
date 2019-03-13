import pygame
from pygame.sprite import OrderedUpdates
from threading import Lock
from collections import namedtuple


lock = Lock()

class TWOrderedUpdates(OrderedUpdates): # массив спрайтов, в тоже время дающий доступ к любому TWObject'у по его uid'у
    
    def __init__(self):
        self.__uids = {}
        super().__init__()


    def add_(self, sprite):
        with lock:
            self.__uids[sprite.uid] = sprite # дублирующий словарь {TWObject.uid: TWObject}
            self.add(sprite)


    def remove_(self, obj): # может прийти и uid, и TWobject
        if type(obj) == int:
            obj = self.__uids.get(obj, None)
        if obj in self:
            with lock:
                self.remove(obj)


    def fx(self, surf):
        for s in self:
            s.fx(surf)


    def __getitem__(self, uid): #из массива можно выбирать объекты по uid'e, как из словаря
        return self.__uids.get(uid, None)

    
#     def custom_draw(self, surface): # каждому объекту позволено оставить свой след на холсте
#         for sprite in self:
#             sprite.drawings(surface)
        

OBJECTS_POOL = TWOrderedUpdates()


cached_pic = None
last_path = None


def subsurf(dims=None, path='img/game.png', scale=0.39):
    global last_path, cached_pic
    if last_path != path: # если ранее была загружена другая картинка, то загружаем новую
        raw_pic = pygame.image.load(path)
        last_path = path # и сохраняем в кэш
        cached_pic = raw_pic
    else:
        raw_pic = cached_pic
    if dims:
        sub = raw_pic.subsurface(pygame.Rect(*dims)) # вырезаем из картинки нужную область
    else:
        sub = raw_pic
        dims = sub.get_rect()
    return pygame.transform.scale(sub, (int(dims[2]*scale), int(dims[3]*scale)))


# собираем все картиночки
pics = {
	'heart_full': subsurf((670, 0, 65, 65)),
	'heart_empty': subsurf((735, 0, 65, 65)),
	'heart_loot': subsurf((320, 70, 60, 50)),
    'aim_default': subsurf((0, 0, 65, 65)),
    
    'GrapplingHook': subsurf(path='img/1x1.png', scale=1),
	'GrapplingHook_proj': subsurf((104, 0, 64, 30), scale=0.5),
    'GrapplingHook_chain': subsurf((63, 4, 40, 30)),
	'Hammer': subsurf((65, 40, 125, 80)),

	'Pistol': subsurf((70, 132, 110, 55)),
	'Pistol_aim': subsurf((0, 130, 65, 65)),
	'Pistol_proj': subsurf((207, 152, 38, 18)),

	'Shotgun': subsurf((64, 193, 225, 6)),
	'Shotgun_aim': subsurf((0, 197, 60, 62)),
	'Shotgun_proj': subsurf((340, 213, 25, 25)),

	'GrenadeLauncher': subsurf((70, 257, 210, 63)),
	'GrenadeLauncher_aim': subsurf((0, 257, 65, 65)),
	'GrenadeLauncher_proj': subsurf((320, 270, 60, 36)),

	'Ninja': subsurf((115, 328, 200, 52)),
	'Ninja_aim': subsurf((0, 320, 65, 65)),

	'Laser': subsurf((70, 390, 210, 80)),
	'Laser_aim': subsurf((3, 387, 65, 65)),
	'Laser_proj': subsurf((335, 392, 35, 52))
}


class WpnModel(namedtuple('WpnModel', [
    'img', # картинка оружия
    'aim', # картинка прицела
    'proj', # картинка снаряда
    'dmg', # урон от снаряда, измеряется в хп (сердце/броня)
    'name', # название модели
    'splash_r', # радиус сплеша
    'flatness', # настильность (0 - 1, насколько снаряд не подвержен гравитации)
    'speed', # скорость полёта снаряда
    'rate', # скорострельность (промежуток между выстрелами)
    'rot', # угол поворота оружия при его отрисовке (если None, то поворачивается вслед за мышкой)
], defaults=(0,0,0,0,0,0,0,0,0,None))):


    def picturize(self, w_name):
        fields = {}
        fields['name'] = w_name
        fields['img'] = pics.get(w_name, None)
        for fld in ['aim', 'proj']: # если нет полей aim, proj, то устанавливаем их при наличии изображения
            fields[fld] = pics.get('%s_%s' % (w_name, fld), None)
        return self._replace(**fields)


wpns = {
    'GrapplingHook': {
        'rate': 0.1,
        'speed': 30,
        'flatness': 1,
    },

    'Hammer': {
        'aim': 'aim_default',
        'dmg': 6,
        'rate': 0.3,
        'rot': -60
    },

    'Pistol': {
        'dmg': 2,
        'flatness': 1,
        'speed': 50,
        'rate': 0.2
    },

    'Shotgun': {
        'dmg': 1,
        'flatness': 1,
        'speed': 40,
        'rate': 0.4
    },

    'GrenadeLauncher': {
        'dmg': 7,
        'splash_r': 3,
        'flatness': 0.2,
        'speed': 23,
        'rate': 0.7
    },

    'Ninja': {
        'dmg': 8,
        'rate': 1,
        'rot': -45
    },

    'Laser': { #TODO: прикрутть эффект лазера
        'dmg': 8,
        'flatness': 1,
        'speed': 999,
        'rate': 2
    }
}

for w_name in wpns:
    wpns[w_name] = WpnModel(**wpns[w_name]).picturize(w_name)


