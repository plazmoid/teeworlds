from objects import PLATFORM_SIZE, DefaultBlock, JumperBlock, Player
#from pygame import Rect
from threading import Thread
import pygame
import re
import logging

SCR_W_COEFF = 30
SCR_H_COEFF = 16
PF_SIZE = PLATFORM_SIZE
SCR_SIZE = (PF_SIZE*SCR_W_COEFF, PF_SIZE*SCR_H_COEFF)

logging.basicConfig(level=logging.DEBUG)

class GameEngine(Thread):
    
    curr_level = 0
    logger = logging.getLogger(__name__)
    
    def __init__(self, nlvl=1):
        super().__init__()
        GameEngine.curr_level = nlvl
        level = LevelBuilder()
        level.build(nlvl)
        self.loop = True
        self.start()

    def run(self):
        while self.loop:
            self._cycle_body()
            pygame.time.wait(12)
    
    def _cycle_body(self):
        raise NotImplementedError
    
    @staticmethod
    def createPlayer(coords=None):
        return Player(coords if coords else [100, 200])
            

class LevelBuilder:

    def __init__(self):
        self.pattern = re.compile(r'-*?\d+?(?:\:-*?\d+\W|\W)')
        self.blocks = {
            '#': DefaultBlock,
            '!': JumperBlock
        }

    def __normalize(self, s_coord):
        s_coord = int(s_coord)
        if s_coord < 0:
            s_coord += SCR_W_COEFF
        return s_coord

    def __unpack(self, level):
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

    def build(self, nlevel):
        by = 0
        for row in self.__unpack(nlevel):
            for bx, block in row.items():
                bpoint = [bx*PF_SIZE, by*PF_SIZE]
                self.blocks[block](bpoint)
            by += 1
            
'''
class Camera():
    def __init__(self, w, h):
        self.camera = Rect(0, 0, w, h)
    
    def apply(self, target):
        return target.rect.move(self.camera.topleft)

    def update(self, target):
        l, t, _, _ = target
        _, _, w, h = self.camera
        l, t = -l+WIN_WIDTH / 2, -t+WIN_HEIGHT / 2
    
        l = min(0, l)
        l = max(-(self.camera.width-WIN_WIDTH), l)
        t = max(-(self.camera.height-WIN_HEIGHT), t)
        t = min(0, t)

        return Rect(l, t, w, h)       
    
'''