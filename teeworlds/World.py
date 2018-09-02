import re
from Entities import Player
import Objects

SCR_W_COEFF = 30
SCR_H_COEFF = 16
PF_SIZE = Objects.PLATFORM_SIZE
SCR_SIZE = (PF_SIZE*SCR_W_COEFF, PF_SIZE*SCR_H_COEFF)

class LevelBuilder:
    
    def __init__(self):
        self.pattern = re.compile(r'-*?\d+?(?:\:-*?\d+\W|\W)')
        self.blocks = {'#': Objects.Block}

    def _normalize(self, s_coord):
        s_coord = int(s_coord)
        if s_coord < 0:
            s_coord += SCR_W_COEFF
        return s_coord

    def _unpack(self, level):
        self.result = {}
        with open('lvl%d.txt' % level, 'r') as fi:
            for row in fi:
                self.result.clear()
                for itm in self.pattern.findall(row):
                    rawblock = itm[-1]
                    itm = itm[:-1]
                    if ':' in itm:
                        pos = list(map(self._normalize, itm.split(':')))
                        for i in range(pos[0], pos[1]+1):
                            self.result[i] = rawblock
                    else:
                        self.result[self._normalize(itm)] = rawblock
                yield self.result

    def build(self, nlevel):
        by = 0
        for row in self._unpack(nlevel):
            for bx, block in row.items():
                bpoint = [bx*PF_SIZE, by*PF_SIZE]
                self.blocks[block](bpoint)
            by += 1


# def eventsHandler():
#     global mainloop
#     e = pygame.event.poll()
#     if e.type == pygame.QUIT:
#         mainloop = False
#     elif e.type == pygame.KEYDOWN:
#         if e.key == pygame.K_LEFT or e.key == pygame.K_a:
#             hero.keydir[0] = -1
#         elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
#             hero.keydir[0] = 1
#         elif e.key == pygame.K_UP or e.key == pygame.K_w:
#             hero.keydir[1] = -1
#         elif e.key == pygame.K_ESCAPE:
#             mainloop = False
#         elif e.key == pygame.K_F1:
#             hero.rect.center = (100, 150)
#             hero.yvel = 0
# 
#     elif e.type == pygame.KEYUP:
#         if e.key == pygame.K_LEFT or e.key == pygame.K_a:
#             hero.keydir[0] = 0
#         elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
#             hero.keydir[0] = 0
#         elif e.key == pygame.K_UP or e.key == pygame.K_w:
#             hero.keydir[1] = 0

#     mouse_pos = pygame.mouse.get_pos()
#     if pygame.mouse.get_pressed()[0]:
#         hero.moveAfterMouse(mouse_pos)
#     hero.lookOnMouse(mouse_pos)

# while True:
#     pygame.display.set_caption('dir: %s, xy: %s, vel: %s, %s' % (hero.dir, [hero.rect.x, hero.rect.y], [hero.xvel, round(hero.yvel, 2)], hero.onGround))
#     eventsHandler()
#     screen.fill(pygame.Color('white'))
#     Objects.OBJECTS_POOL.update()
#     Objects.OBJECTS_POOL.draw(screen)
#     window.blit(screen, (0,0))
#     pygame.display.flip()
#     pygame.time.wait(12)

def create_player(coords=None):
    return Player(coords if coords else [100, 200])
