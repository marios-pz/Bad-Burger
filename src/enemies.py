import types
import pygame as pg
import random
from src.utils import *
from os import listdir
import src.pathfinder as pfd
from src.tiles import ColliderTiles as CT


class Enemy1:

    def __init__(self, screen, player, tile_map, dep_pos, type):

        self.screen = screen
        self.tile_map = tile_map

        self.surface = pg.Surface((32, 32))
        self.rect = self.surface.get_rect(topleft=(dep_pos[0] * 32, dep_pos[1] * 32))
        self.index = list(dep_pos)

        self.player_grid = player.player_grid
        self.player = player

        self.direction = "right"
        self.moving = False
        self.velocity = 5

        self.TLS_Y = tile_map.TLS_Y
        self.TLS_X = tile_map.TLS_X

        self.target = None
        self.tr_dir_x = None
        self.tr_dir_y = None
        self.nearest = None
        self.nr_id = None
        self.nr_obj = None

        self.anim_down = [load_alpha(f"data/assets/enemy1_down/{file}") for file in listdir("data/assets/enemy1_down")]
        self.anim_up = [load_alpha(f"data/assets/enemy1_up/{file}") for file in listdir("data/assets/enemy1_up")]
        self.current_time = pg.time.get_ticks()
        self.delay_anim = 0
        self.index_anim = 0

        self.delayed = 0
        self.delaying = False

    def break_ice(self, first_cell):
        self.player_grid = self.player.player_grid

        is_available = self.is_ice(first_cell)
        if is_available[0]:
            is_available[1].destruct(0, first_cell)
        self.player.player_grid[first_cell[1]][first_cell[0]] = 0
        self.player_grid = self.player.player_grid
        self.delaying = True
        self.delayed = pg.time.get_ticks()

    def is_ice(self, index_):
        if type(self.tile_map.collider_tiles[index_[1]][index_[0]]) is CT.IceBlock:
            return True, self.tile_map.collider_tiles[index_[1]][index_[0]]
        return False, None

    def eat_fruit(self, index):
        self.fruits.grid[index[1]][index[0]] = None

    def move_right(self):
        if not self.moving:
            if not self.coll_right():
                self.index[0] += 1
                self.moving = True
            self.direction = "right"

    def move_left(self):
        if not self.moving:
            if not self.coll_left():
                self.index[0] -= 1
                self.moving = True
            self.direction = "left"

    def move_up(self):
        if not self.moving:
            if not self.coll_up():
                self.index[1] -= 1
                self.moving = True
            self.direction = "up"

    def move_down(self):
        if not self.moving:
            if not self.coll_down():
                self.index[1] += 1
                self.moving = True
            self.direction = "down"

    def coll_right(self):
        id_x, id_y = self.index
        if id_x + 1 > len(self.player_grid[id_y]) - 2 or self.player_grid[id_y][id_x + 1] == 1:
            return True
        return False

    def coll_left(self):
        id_x, id_y = self.index
        if id_x - 1 < 1 or self.player_grid[id_y][id_x - 1] == 1:
            return True
        return False

    def coll_up(self):
        id_x, id_y = self.index
        if id_y - 1 < 1 or self.player_grid[id_y - 1][id_x] == 1:
            return True
        return False

    def coll_down(self):
        id_x, id_y = self.index
        if id_y + 1 > len(self.player_grid) - 2 or self.player_grid[id_y + 1][id_x] == 1:
            return True
        return False

    def manage_animation(self):
        if self.direction == "right":
            if self.rect.x + self.velocity >= self.index[0] * self.TLS_X:
                self.moving = False
                self.rect.x += (self.index[0] * self.TLS_X - self.rect.x)
            else:
                self.rect.x += self.velocity
        elif self.direction == "left":
            if self.rect.x - self.velocity <= self.index[0] * self.TLS_X:
                self.moving = False
                self.rect.x -= (self.rect.x - self.index[0] * self.TLS_X)
            else:
                self.rect.x -= self.velocity
        elif self.direction == "up":
            if self.rect.y - self.velocity <= self.index[1] * self.TLS_Y:
                self.moving = False
                self.rect.y -= (self.rect.y - self.index[1] * self.TLS_Y)
            else:
                self.rect.y -= self.velocity
        elif self.direction == "down":
            if self.rect.y + self.velocity >= self.index[1] * self.TLS_Y:
                self.moving = False
                self.rect.y += (self.index[1] * self.TLS_Y - self.rect.y)
            else:
                self.rect.y += self.velocity

    def move(self):
        if self.moving:
            self.manage_animation()
        elif not self.radius_player_detection():
            self.velocity = 3

            if not self.coll_right() and self.direction == "right":
                self.move_right()
            elif not self.coll_left() and self.direction == "left":
                self.move_left()
            elif not self.coll_up() and self.direction == "up":
                self.move_up()
            elif not self.coll_down() and self.direction == "down":
                self.move_down()

            else:
                move_choice = random.randint(1, 4)
                if move_choice == 1:
                    self.move_down()
                elif move_choice == 2:
                    self.move_right()
                elif move_choice == 3:
                    self.move_left()
                else:
                    self.move_up()
        else:
            self.velocity = 3

            path = pfd.init_pathfinder(self.index, self.player.index, self.player.player_grid)
            if path is False:
                
                grid_without_ice = [[0 if type(block) is CT.IceBlock or block is None else 1 for block in self.tile_map.collider_tiles[_1]] for _1 in range(len(self.player_grid))]
                for i in grid_without_ice:
                    print(i)    

                print("")

                for i in self.player_grid:
                    print(i)
                
                second_path = pfd.init_pathfinder(self.index, self.player.index, grid_without_ice)
                dx, dy = self.index[0]-second_path[1][0], self.index[1]-second_path[1][1]

                if dx < 0:
                    if not self.coll_right():
                        self.move_right()
                    else:
                        self.break_ice([self.index[0]+1, self.index[1]])
                elif dx > 0:
                    if not self.coll_left():
                        self.move_left()
                    else:
                        self.break_ice([self.index[0]-1, self.index[1]])
                elif dy < 0:
                    if not self.coll_down():
                        self.move_down()
                    else:
                        self.break_ice([self.index[0], self.index[1]+1])
                else:
                    if not self.coll_up():
                        self.move_up()
                    else:
                        self.break_ice([self.index[0], self.index[1]+1])

            elif type(path) is list:

                dx, dy = self.index[0]-path[1][0], self.index[1]-path[1][1]
                
                if dx < 0:
                    self.move_right()
                elif dx > 0:
                    self.move_left()
                elif dy < 0:
                    self.move_down()
                else:
                    self.move_up()

    def radius_player_detection(self):
        dx, dy = abs(self.player.index[0]-self.index[0]), abs(self.player.index[1]-self.index[1])
        if dx <= 5 and dy <= 5:
            return True
        return False

    def animate(self):
        self.current_time = pg.time.get_ticks()

        if self.moving:

            if self.current_time - self.delay_anim > 70:
                self.delay_anim = self.current_time

                if self.direction == "down":
                    self.index_anim = (self.index_anim + 1) % len(self.anim_down)
                    self.surface = self.anim_down[self.index_anim]
                elif self.direction == "up":
                    self.index_anim = (self.index_anim + 1) % len(self.anim_up)
                    self.surface = self.anim_up[self.index_anim]
                elif self.direction == "right":
                    self.index_anim = (self.index_anim + 1) % len(self.anim_down)
                    self.surface = self.anim_down[self.index_anim]
                elif self.direction == "left":
                    self.index_anim = (self.index_anim + 1) % len(self.anim_down)
                    self.surface = self.anim_down[self.index_anim]
                    


    def update(self):
        self.current_time = pg.time.get_ticks()

        self.player_grid = self.player.player_grid
        if not self.delaying:
            self.move()
            self.animate()
        else:
            if self.current_time - self.delayed > 500:
                self.delaying = False

        self.screen.blit(self.surface, self.rect)
