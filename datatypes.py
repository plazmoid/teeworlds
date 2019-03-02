import pygame

    
class PicModel:
    
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
    

class PicContainer: # удобный резчик картиночек
        
    cached_Pic = None # последний загруженный экземпляр класса Pic
    
    def __init__(self):
        self.pics = {}
                
        
    def add(self, picname, path, dims):
        self.pics[picname] = PicModel(picname, path, dims)

    
    def get(self, picname):
        return self.pics[picname].load()
    
    
# собираем все картиночки
piccontainer = PicContainer()
piccontainer.add('heart_full', 'img/game.png', (670, 0, 65, 65))
piccontainer.add('heart_empty', 'img/game.png', (735, 0, 65, 65))
piccontainer.add('heart_loot', 'img/game.png', (320, 70, 60, 50))
piccontainer.add('hook', 'img/game.png', (63, 0, 110, 32))
piccontainer.add('hammer', 'img/game.png', (65, 40, 125, 80))
piccontainer.add('aim_default', 'img/game.png', (0, 0, 65, 65))
piccontainer.add('aim_gun', 'img/game.png', (0, 130, 65, 65))


class WpnModel:
    
    def __init__(self, name, img, aimg):
        self.img = None
        self.aimg = None
    




    