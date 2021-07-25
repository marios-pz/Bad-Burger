import pygame as pg



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