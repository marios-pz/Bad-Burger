import pygame as pg
from pygame.draw import line
import src.enemies as enemies


class EnemyManager:

    def __init__(self, screen, player, tile_map):
        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()

        self.tile_map = tile_map

        self.fruits = []
        self.enemies = [enemies.Enemy1(self.screen, player, tile_map, self.fruits, (1, 2)),
                        enemies.Enemy1(self.screen, player, tile_map, self.fruits, (5, 6)),
                        enemies.Enemy1(self.screen, player, tile_map, self.fruits, (10, 9))]

        self.level = None
        self.state = 0

    def change_fruit_state(self):
        self.state += 1
        self.init_grid()

    def init_level(self, level):
        self.level = level
        self.state = 0
        self.init_grid()

    def init_grid(self):
        with open(self.level.path_frtuits[self.state], "r") as f:
            datas = f.readlines()

        self.fruits = []
        lines = []
        for row in datas:
            row = (row.replace(" ", "")).strip()
            for col in row:
                lines.append(0) if col == "0" else lines.append(1)
            self.fruits.append(lines)

    def update(self) -> None:

        for enemy in self.enemies:
            enemy.update()

        