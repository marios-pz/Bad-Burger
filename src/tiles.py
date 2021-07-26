import pygame as pg
from src.utils import *
import copy



class GroundTiles:
    # Parent Class to store all the ground tiles

    # Subclasses for each ground tile
    class Grass:

        def __init__(self, screen, size, coordinates):

            self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()

            self.image = pg.Surface(size)
            self.image.fill((0, 255, 0))

            self.rect = self.image.get_rect(topleft=coordinates)

        def update(self):
            self.screen.blit(self.image, self.rect)

    class Rock:

        def __init__(self, screen, size, coordinates):
            self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()
            self.image = pg.Surface(size)
            self.image.fill((100, 100, 100))
            self.rect = self.image.get_rect(topleft=coordinates)

        def update(self):
            self.screen.blit(self.image, self.rect)


class ColliderTiles:

    class IceBlock:

        def __init__(self, screen, size, coordinates, happening, delay_happening):

            self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()
            self.happening = happening
            
            self.image = load_alpha("data/assets/iceblock.png")
            #self.image = resize(self.image, size) 
            self.image.set_alpha(199)

            self.rect = self.image.get_rect(bottomleft=coordinates+pg.Vector2(0, 32))

            self.current_time = pg.time.get_ticks()
            self.delay_happening = pg.time.get_ticks()+delay_happening
            self.delay_h = pg.time.get_ticks()
            self.delay = 0
            self.destructing = False
            self.cell = [0, 0]

        def destruct(self, cascade, cell):
            self.delay = pg.time.get_ticks() + cascade*100
            self.destructing = True
            self.cell = copy.copy(cell)

        def update(self):
            self.current_time = pg.time.get_ticks()
            if self.destructing:
                if self.current_time - self.delay > 500:
                    return "kill", self.cell # Else, we are playing a animation

            if self.happening:
                if self.current_time - self.delay_happening > 100:
                    self.happening = False                         
            else:
                self.screen.blit(self.image, self.rect)
            return None, None