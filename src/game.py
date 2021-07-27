from src.utils import *
import pygame as pg
import time
import src.level_selector as level_selector
import src.ui as ui
import src.tilemap as tilemap
import src.player as player
import src.menu as menu
import src.levels as lvl


class Game:

    def __init__(self):

        # ------------------- SCREEN VARIABLES ----------------------------- #
        self.W, self.H = 640, 480
        self.screen = pg.display.set_mode((self.W, self.H), pg.SCALED)

        # ------------------- GAME STATE VARIABLES ------------------------- #
        self.running: bool = True
        self.running_menu: bool = True
        self.running_game: bool = False
        self.running_level_selector: bool = False

        # --------------- VARIABLES ---------------------------------------- #
        self.settings = get_json("src/settings")
        self.clock_ui: pg.surface.Surface = load_alpha("data/assets/clock/clock_ui.png")
        self.font_60: pg.font.Font = pg.font.Font(None, 60)
        self.font_50: pg.font.Font = pg.font.Font(None, 50)
        self.font_40: pg.font.Font = pg.font.Font(None, 40)
        self.font_30: pg.font.Font = pg.font.Font(None, 30)
        self.font_20: pg.font.Font = pg.font.Font(None, 20)
        self.last_time: float = time.time()
        self.dt: float = None

        # ------------------- TILE MAP ------------------------------------- #
        self.tile_map = tilemap.TileMap(self.screen, 32)

        # ------------------- CLASS INSTANCES ------------------------------ #
        self.clock = pg.time.Clock()
        self.ui: ui.UI = ui.UI(self.settings["FPS"])
        self.level_selector: level_selector.LevelSelector = level_selector.LevelSelector(self.screen, self.settings, self.clock, available_levels=40, last_level_unlocked=10)
        self.menu = menu.Menu(self.screen, self.clock)

        self.player = player.Player(self.tile_map, self.screen)

        self.levels = [
            lvl.Level1,
            lvl.Level2,
            lvl.Level3,
            lvl.Level4,
            lvl.Level5,
            lvl.Level6,
            lvl.Level7,
            lvl.Level8,
            lvl.Level9,
            lvl.Level10
        ]

    @staticmethod
    def __quit__():
        # quit the entire program
        pg.quit()
        raise SystemExit

    def __returnToMenu__(self):  # start running the menu
        self.running_game, self.running_menu, self.running_level_selector = False, True, False

    def __startGame__(self, level):  # start running the game
        self.player.init_level(self.levels[level-1])
        self.tile_map.init_level(self.levels[level-1])
        self.running_game, self.running_menu, self.running_level_selector = True, False, False

    def __startLevelSelector__(self):  # it starts the level selector
        self.running_game, self.running_menu, self.running_level_selector = False, False, True

    def run_menu(self):
        self.menu.run(self.settings["FPS"])
        self.__startLevelSelector__()
        self.settings = get_json("src/settings")

    def run_level_selector(self):
        response = self.level_selector.run(self.settings["FPS"])
        if response == "back":
            self.__returnToMenu__()
            return
        elif isinstance(response, int):
            self.__startGame__(self.level_selector.selected_level)
        # print(self.level_selector.selected_level) it will print the level that the player chose to play

    def show_above_player(self):
        grid = self.player.player_grid

        if self.player.index[1] + 1 < len(grid):
            if self.player.index[0] - 1 >= 0:
                cell1 = [self.player.index[0]-1, self.player.index[1]+1]
                block = self.get_block(cell1)
                if block is not None:
                    return True

            cell2 = [self.player.index[0], self.player.index[1]+1]
            block = self.get_block(cell2)
            if block is not None:
                return True

            if self.player.index[0] + 1 < len(grid[self.player.index[1]]):
                cell3 = [self.player.index[0]+1, self.player.index[1]+1]
                block = self.get_block(cell3)
                if block is not None:
                    return True
        return False

    def get_block(self, index):

        for tiles in self.tile_map.collider_tiles:
            for tile in tiles:
                if tile is not None:

                    if tile.rect.collidepoint(index[0]*self.tile_map.TLS_X, index[1]*self.tile_map.TLS_Y):
                        return tile

    def update_player_and_tiles(self):

            self.tile_map.update_ground()

            if not self.show_above_player():
                update_tl_map_col = self.tile_map.update_colliders()
                # check if there are blocks to remove from the player grid
                if update_tl_map_col is not None:
                    self.player.reset_ice_blocks(update_tl_map_col)

                update_pl = self.player.update(self.dt)
                if update_pl is not None:
                    pass
            else:
                update_pl = self.player.update(self.dt)
                if update_pl is not None:
                    pass

                update_tl_map_col = self.tile_map.update_colliders()
                # check if there are blocks to remove from the player grid
                if update_tl_map_col is not None:
                    self.player.reset_ice_blocks(update_tl_map_col)

    def run_game(self):
        self.ui.reset(120)
        while self.running_game:
            self.clock.tick(self.settings["FPS"])
            self.ui.tick()
            self.dt = time.time() - self.last_time
            self.dt *= 60
            self.last_time = time.time()

            for e in pg.event.get():
                e_pl = self.player.handle_events(e)
                if type(e_pl) is list:
                    self.tile_map.add_ices(e_pl)

                if e.type == pg.QUIT:
                    self.__quit__()
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_ESCAPE:
                        self.__returnToMenu__()

            self.screen.fill((255, 255, 255))

            self.update_player_and_tiles()

            self.screen.blit(self.clock_ui, (self.W - self.clock_ui.get_width() - 5, 5))
            label = self.font_30.render(self.ui.get_time() if self.ui.get_time() else "00:00", True, (0, 0, 0))
            self.screen.blit(label, (self.W - label.get_width() - 13, 10))
            if self.ui.get_time():
                self.ui.clock_animation.animate()
            self.ui.clock_animation.update(self.screen)

            pg.display.update()

    def run(self):
        while self.running:

            if self.running_menu:
                self.run_menu()

            elif self.running_level_selector:
                self.run_level_selector()

            elif self.running_game:
                self.run_game()

            else:
                self.__quit__()
