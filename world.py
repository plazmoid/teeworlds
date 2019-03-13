from configs import SCR_W_COEFF, PLATFORM_SIZE
from threading import Thread
from objects import real
import pygame
import re
import logging


logging.basicConfig(level=logging.INFO)

class TWEngine(Thread): # здесь крутится игровой цикл на сервере и клиенте
    
    logger = logging.getLogger(__name__)
    
    def __init__(self, nlvl):
        super().__init__()
        pygame.init()
        pygame.font.init()
        pygame.event.set_blocked(pygame.MOUSEMOTION) # чтоб движения мышки не забивали очередь событий
        self.__lvl_builder = LevelBuilder()
        self.__lvl_builder.build(nlvl)
        self.loop = True
        self.start()

    def run(self):
        while self.loop:
            self._e_cycle_body()
            pygame.time.wait(12)
    
    # все нужные действия в цикле будут выполняться отнаследованными клиентом и сервером по-разному
    def _e_cycle_body(self): 
        raise NotImplementedError
    
    # спавн игровых объектов с учётом того, что 1 единица на координатной сетке = 1 кубик (размеры прописаны в конфиге)
    @staticmethod
    def spawn(TWobj, coords, *args, **kwargs): 
        x, y, *sizes = coords
        return TWobj([x*PLATFORM_SIZE, y*PLATFORM_SIZE] + sizes, *args, **kwargs)
    
    
    @property
    def lvl(self):
        return self.__lvl_builder.CURR_LVL    
    

class LevelBuilder: # парсер уровней

    CURR_LVL = 0
    
    def __init__(self):
        self.pattern = re.compile(r'-*?\d+?(?:\:-*?\d+\W|\W)')
        self.level_map = {} # {(x, y): block}
        self.blocks = {
            '#': real.DefaultBlock,
            '!': real.JumperBlock
        }
        

    def __normalize(self, s_coord):
        s_coord = int(s_coord)
        if s_coord < 0:
            s_coord += SCR_W_COEFF
        return s_coord


    def __unpack(self, level): # распаковка совершенно упоротого придуманного формата
        self.result = {}
        with open('lvl%d.txt' % level, 'r') as fi:
            for row in fi:
                self.result.clear()
                for itm in self.pattern.findall(row):
                    rawblock = itm[-1]
                    itm = itm[:-1]
                    if ':' in itm:
                        pos = list(map(self.__normalize, itm.split(':')))
                        for i in range(pos[0], pos[1]+1):
                            self.result[i] = rawblock
                    else:
                        self.result[self.__normalize(itm)] = rawblock
                yield self.result
                

    def build(self, nlvl):
        LevelBuilder.CURR_LVL = nlvl
        by = 0
        for row in self.__unpack(nlvl):
            for bx, block in row.items():
                TWEngine.spawn(self.blocks[block], (bx, by)) # создание кубиков уровня
            by += 1
            
            
            