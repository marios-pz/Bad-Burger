import pygame as pg
from src.utils import *



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

        def __init__(self, screen, size, coordinates):

            self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()
            
            
            self.image = load("data/assets/ice_block.png")
            self.image = resize(self.image, size) 

            """self.image = pg.Surface(size)
            self.image.fill((0, 100, 255))"""

            self.rect = self.image.get_rect(topleft=coordinates)

        def update(self):
            self.screen.blit(self.image, self.rect)