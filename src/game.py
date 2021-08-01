from src.utils import *
import pygame as pg
import time
import src.fruits as fruits
import src.level_selector as level_selector
import src.ui as ui
import src.tilemap as tilemap
import src.player as player
import src.menu as menu
import src.levels as lvl
import src.enemy_manager as enemy_manager
import src.pause as pause
import src.winning_screen as winning_screen


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
        self.font_60: pg.font.Font = pg.font.Font("data/fonts/Minecraft.ttf", 60)
        self.font_50: pg.font.Font = pg.font.Font("data/fonts/Minecraft.ttf", 50)
        self.font_40: pg.font.Font = pg.font.Font("data/fonts/Minecraft.ttf", 40)
        self.font_30: pg.font.Font = pg.font.Font("data/fonts/Minecraft.ttf", 30)
        self.font_20: pg.font.Font = pg.font.Font("data/fonts/Minecraft.ttf", 20)
        self.font_10: pg.font.Font = pg.font.Font("data/fonts/Minecraft.ttf", 10)
        self.last_time: float = time.time()
        self.dt: float = None
        self.pausing = False
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

        # ------------------- TILE MAP ------------------------------------- #
        self.tile_map = tilemap.TileMap(self.screen, 32)

        # ------------------- CLASS INSTANCES ------------------------------ #
        self.clock = pg.time.Clock()
        self.fruits: fruits.FruitMap = fruits.FruitMap(self.screen, self.tile_map.TILE_SIZE, (30, 30))
        self.player = player.Player(self.tile_map, self.fruits, self.screen)
        self.ui: ui.UI = ui.UI(self.screen, self.fruits, self.settings["FPS"], self.player)
        self.level_selector: level_selector.LevelSelector = level_selector.LevelSelector(self.screen, self.settings, self.clock, available_levels=40, last_level_unlocked=10)
        self.menu = menu.Menu(self.screen, self.clock)
        self.pause = pause.Pause(self.screen)
        self.enemy_manager = enemy_manager.EnemyManager(self.screen, self.player, self.tile_map, self.fruits)
        self.winning_screen = None
        self.victory = None
        self.current_level = None
        self.delay = 0
        self.end = False

    @staticmethod
    def __quit__():
        # quit the entire program
        pg.quit()
        raise SystemExit

    def __returnToMenu__(self):  # start running the menu
        self.running_game, self.running_menu, self.running_level_selector = False, True, False

    def __startGame__(self, level):  # start running the game
        self.victory = None
        self.current_level = level
        self.player.init_level(self.levels[level-1])
        self.tile_map.init_level(self.levels[level-1])
        self.fruits.init_level(self.levels[level-1])  # it loads the first layer of fruits
        self.enemy_manager.init_level(self.levels[level-1])
        self.running_game, self.running_menu, self.running_level_selector = True, False, False
        self.end = False

    def restart_level(self):
        self.__startGame__(self.current_level)

    def next_level(self):
        if self.current_level < len(self.levels)-1:
            self.current_level += 1
            self.player.moving = False
            self.player.victory = False
            self.__startGame__(self.current_level)

    def __startLevelSelector__(self):  # it starts the level selector
        self.running_game, self.running_menu, self.running_level_selector = False, False, True

    def __initVictory__(self):
        self.delay = pg.time.get_ticks()
        self.victory = True
        self.player.moving = False
        self.player.victory = True
        self.enemy_manager.set_victory(False)
        self.winning_screen = winning_screen.WinningScreen(self.screen, True, self.player.score)

    def __initDefeat__(self):
        self.delay = pg.time.get_ticks()
        self.victory = False
        self.player.moving = False
        self.player.victory = False
        self.player.dying = True
        self.enemy_manager.set_victory(False)
        self.winning_screen = winning_screen.WinningScreen(self.screen, False, self.player.score)

    def set_pause_active(self):
        self.pausing = not self.pausing

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

    def get_block(self, index):

        for tiles in self.tile_map.collider_tiles:
            for tile in tiles:
                if tile is not None:

                    if tile.rect.collidepoint(index[0]*self.tile_map.TLS_X, index[1]*self.tile_map.TLS_Y):
                        return tile

    def update_player_fruits_tiles(self):

        self.tile_map.update_ground()

        fruit_updating = self.fruits.update()
        if fruit_updating == "victory":
            
            self.__initVictory__()

        self.player.update(self.dt, self.enemy_manager.enemies, self.ui)
        self.enemy_manager.update()

        if self.victory is None:
            for enemy in self.enemy_manager.enemies:
                if enemy.index == self.player.index:
                    self.__initDefeat__()
                    

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
                if isinstance(e_pl, list):
                    self.tile_map.add_ices(e_pl)

                if e.type == pg.QUIT:
                    self.__quit__()
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_ESCAPE:

                        self.set_pause_active()

            self.screen.fill((255, 255, 255))

            self.update_player_fruits_tiles()

            self.screen.blit(self.clock_ui, (self.W - self.clock_ui.get_width() - 5, 5))
            label = self.font_20.render(self.ui.get_time() if self.ui.get_time() else "00:00", True, (0, 0, 0))
            self.screen.blit(label, (self.W - label.get_width() - 17, 10))
            if self.ui.get_time():
                self.ui.clock_animation.animate()
            self.ui.clock_animation.update(self.screen)

            self.ui.update()
            if self.pausing:
                response = self.pause.run(self, self.settings["FPS"])
                if response == "resume":
                    self.set_pause_active()
                elif response == "quit":
                    self.set_pause_active()
                    self.__returnToMenu__()

                self.pause.update()
            if self.end:
                response = self.winning_screen.run(self, self.settings["FPS"])
                if response == "restart":
                    self.restart_level()
                elif response == "next level":
                    self.next_level()
                elif response == "quit":
                    self.__returnToMenu__()
                self.winning_screen.update()

            if self.victory is not None:
                print(pg.time.get_ticks() - self.delay)
                if pg.time.get_ticks() - self.delay > 2000:
                    self.end = True

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
