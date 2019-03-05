import pygame
from pygame.sprite import OrderedUpdates
from threading import Lock
from collections import namedtuple


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


    def __getitem__(self, uid): #из массива можно выбирать объекты по uid'e, как из словаря
        return self.__uids.get(uid, None)

    
    def custom_draw(self, surface): # каждому объекту позволено оставить свой след на холсте
        for sprite in self:
            sprite.drawings(surface)
        

OBJECTS_POOL = TWOrderedUpdates()
        
def get_objects_pool():
    return OBJECTS_POOL # на всякий случай



cached_pic = None
last_path = None
scale_coeff = 0.36


def cutter(dims, path='img/game.png'):
    global last_path, cached_pic, scale_coeff
    if last_path != path: # если была загружена другая картинка, то загружаем новую
        raw_pic = pygame.image.load(path)
        last_path = path # и сохраняем в кэш
        cached_pic = raw_pic
    else:
        raw_pic = cached_pic
    sub = raw_pic.subsurface(pygame.Rect(*dims)) # вырезаем из картинки нужную область
    return pygame.transform.scale(sub, (int(dims[2]*scale_coeff), int(dims[3]*scale_coeff)))


# собираем все картиночки
pics = {}
pics['heart_full'] = cutter((670, 0, 65, 65))
pics['heart_empty'] = cutter((735, 0, 65, 65))
pics['heart_loot'] = cutter((320, 70, 60, 50))
pics['hook'] = cutter((63, 0, 110, 32))
pics['hammer'] = cutter((65, 40, 125, 80))
pics['aim_default'] = cutter((0, 0, 65, 65))

pics['pistol'] = cutter((70, 132, 110, 55))
pics['pistol_aim'] = cutter((0, 130, 65, 65))
pics['pistol_proj'] = cutter((207, 152, 38, 18))

pics['rifle'] = cutter((64, 193, 225, 6))
pics['rifle_aim'] = cutter((0, 197, 60, 62))
pics['rifle_proj'] = cutter((340, 213, 25, 25))

pics['grenade_launcher'] = cutter((70, 257, 210, 63))
pics['grenade_launcher_aim'] = cutter((0, 257, 65, 65))
pics['grenade_launcher_proj'] = cutter((320, 270, 60, 36))

pics['ninja'] = cutter((115, 328, 200, 52))
pics['ninja_aim'] = cutter((0, 320, 65, 65))

pics['laser'] = cutter((70, 390, 210, 80))
pics['laser_aim'] = cutter((3, 387, 65, 65))
pics['laser_proj'] = cutter((335, 392, 35, 52))


WpnModel = namedtuple('TTX', [
    'img', # картинка оружия
    'aim', # картинка прицела
    'proj', # картинка снаряда
    'dmg', # урон от снаряда, измеряется в хп (сердце/броня)
    'splash_r', # радиус сплеша (в пикселях)
    'flatness', # настильность (0 - 1, насколько снаряд не подвержен гравитации)
    'speed', # скорость полёта снаряда
    'melee', # урон в ближнем бою
    'rate', # скорострельность (выстрел раз в rate секунд)
], defaults=('', '', '', 0, 0, 0, 0, 0))


    
wpns = {}

wpns['GrapplingHook'] = WpnModel(
    img=pics['hook'],
    rate=0.2
)

wpns['Hammer'] = WpnModel(
    img=pics['hammer'],
    aim=pics['aim_default'],
    melee=6,
    rate=0.3
)

wpns['Pistol'] = WpnModel(
    img=pics['pistol'],
    aim=pics['pistol_aim'],
    proj=pics['pistol_proj'],
    dmg=2,
    flatness=1,
    speed=40,
    rate=0.2
)

wpns['Shotgun'] = WpnModel(
    img=pics['rifle'],
    aim=pics['rifle_aim'],
    proj=pics['rifle_proj'],
    dmg=4,
    flatness=1,
    speed=40,
    rate=0.4
)

wpns['GrenadeLauncher'] = WpnModel(
    img=pics['grenade_launcher'],
    aim=pics['grenade_launcher_aim'],
    proj=pics['grenade_launcher_proj'],
    dmg=7,
    splash_r=5,
    flatness=0.5,
    speed=25,
    rate=1
)

wpns['Ninja'] = WpnModel(
    img=pics['ninja'],
    aim=pics['ninja_aim'],
    melee=8,
    rate=1
)

wpns['Laser'] = WpnModel(
    img=pics['laser'],
    aim=pics['laser_aim'],
    proj=pics['laser_proj'], # NOPE
    dmg=8,
    flatness=1,
    speed=999,
    rate=2
)




    