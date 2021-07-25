import pygame as pg
import src.tilemap as tilemap


class Game:

    def __init__(self):
        
        # width, height
        self.w, self.h = 640, 480
        self.screen = pg.display.set_mode((self.w, self.h), pg.SCALED)

        self.running = True
        self.menu = True
        self.game = False

        self.tile_map = tilemap.TileMap(self.screen)

    def __quit__(self):
        pg.quit()
        raise SystemExit

    def __returnToMenu__(self):
        self.game = False
        self.menu = True

    def __startGame__(self):
        self.game = True
        self.menu = False

    def run(self):

        while self.running:

            while self.menu:

                for event in pg.event.get():

                    if event.type == pg.QUIT:
                        self.__quit__()

                    if event.type == pg.KEYDOWN:
                        if event.key == 13: # enter key
                            self.__startGame__()

                self.screen.fill((255, 100, 50))
                
                pg.display.update()

            while self.game:

                for event in pg.event.get():

                    if event.type == pg.QUIT:
                        self.__quit__()

                    if event.type == pg.KEYDOWN:

                        if event.key == pg.K_ESCAPE:
                            self.__returnToMenu__()

                    self.screen.fill((255, 255, 255))
                    self.tile_map.update()

                    pg.display.update()
