import pygame as pg
import src.tilemap as tilemap
import src.player as player
import src.settings as set
import src.menu as menu

class Game:

    def __init__(self):
        
        # ------------------- SCREEN VARIABLES ----------------------------- #
        self.w, self.h = 640, 480
        self.screen = pg.display.set_mode((self.w, self.h), pg.SCALED)

        # ------------------- GAME STATE VARIABLES ------------------------- #
        self.running: bool = True
        self.running_menu: bool = True
        self.running_game: bool = False

        # ------------------- TILE MAP ------------------------------------- #
        self.tile_map = tilemap.TileMap(self.screen)

        # ------------------- CLASS INSTANCES ------------------------------ #
        self.clock = pg.time.Clock()
        self.menu = menu.Menu(self.screen, self.clock)
        
        self.ground = self.tile_map.ground_tiles # I need this for player's pos
        self.player = player.Player(self.ground, 32, self.screen)

    @staticmethod
    def __quit__():
        # quit the entire program
        pg.quit()
        raise SystemExit

    def __returnToMenu__(self): # return from the game to the menu       
        self.running_game, self.running_menu = False, True

    def __startGame__(self): # go from the menu to the game       
        self.running_game, self.running_menu = True, False

    def run_menu(self):
        self.menu.run(set.FPS)
        self.__startGame__()

    def run_game(self):
        while self.running_game:
            self.clock.tick(set.FPS)

            for e in pg.event.get():
                self.player.handle_events(e)
                if e.type == pg.QUIT:
                    self.__quit__()
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_ESCAPE:
                        self.__returnToMenu__()

                self.screen.fill((255, 255, 255))
                self.tile_map.update()
                self.player.update()
                pg.display.update()

    def run(self):
        while self.running:
            if self.running_menu:
                self.run_menu()
            elif self.running_game:
                self.run_game()
            else:
                self.__quit__()