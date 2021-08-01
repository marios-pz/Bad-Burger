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

        self.surface = resizex(load_alpha(f"data/assets/enemy1_down/enemy1_down1.png"),1)
        self.rect = self.surface.get_rect(center=(dep_pos[0] * 32 + 16, dep_pos[1] * 32 + 16)) # Pls move the enemy a little to the left if possible
        self.index = list(dep_pos)

        self.player_grid, self.player = player.player_grid, player
        self.direction = "right" # Default direction
        self.moving =  self.delaying = False
        self.velocity = self.delay_anim = self.index_anim = self.delayed = 0
        self.TLS_Y, self.TLS_X = tile_map.TLS_Y, tile_map.TLS_X
        self.target =  self.tr_dir_x = self.tr_dir_y  = self.nearest = self.nr_id = self.nr_obj = None

        self.anim_down = [resizex(load_alpha(f"data/assets/enemy1_down/{file}"),1) for file in listdir("data/assets/enemy1_down")]
        self.anim_up = [resizex(load_alpha(f"data/assets/enemy1_up/{file}"),1) for file in listdir("data/assets/enemy1_up")]
        self.anim_left = [resizex(load_alpha(f'data/assets/enemy1_side/{file}'), 1) for file in listdir('data/assets/enemy1_side')]
        self.anim_right = [pg.transform.flip(image, True, False).convert_alpha() for image in self.anim_left]
        self.current_time = pg.time.get_ticks()

        self.exclamation_point = load_alpha("data/assets/exlamation_point.png")
        self.delay = 0
        self.showing = False

        self.spot_sound = pg.mixer.Sound('data/detect.wav')
        self.spot_sound.set_volume(0.2)
        self.detect_counter = 0

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
        return id_x + 1 > len(self.player_grid[id_y]) - 2 or self.player_grid[id_y][id_x + 1] == 1

    def coll_left(self):
        id_x, id_y = self.index
        return id_x < 2 or self.player_grid[id_y][id_x - 1] == 1

    def coll_up(self):
        id_x, id_y = self.index
        return id_y < 2 or self.player_grid[id_y - 1][id_x] == 1

    def coll_down(self):
        id_x, id_y = self.index
        return id_y + 1 > len(self.player_grid) - 2 or self.player_grid[id_y + 1][id_x] == 1

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
            self.velocity = 1.5

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
            self.velocity = 2.25 # The speed increases by 75 %

            path = pfd.init_pathfinder(self.index, self.player.index, self.player.player_grid)
            if path is False:
                
                grid_without_ice = [[0 if type(block) is CT.IceBlock or block is None else 1 for block in self.tile_map.collider_tiles[_1]] for _1 in range(len(self.player_grid))]         
                second_path = pfd.init_pathfinder(self.index, self.player.index, grid_without_ice)

                if self.index[0]-second_path[1][0] < 0: # dx
                    if not self.coll_right():
                        self.move_right()
                    else:
                        self.break_ice([self.index[0]+1, self.index[1]])
                elif self.index[0]-second_path[1][0] > 0: # dx
                    if not self.coll_left():
                        self.move_left()
                    else:
                        self.break_ice([self.index[0]-1, self.index[1]])
                elif self.index[1]-second_path[1][1] < 0: # dy
                    if not self.coll_down():
                        self.move_down()
                    else:
                        self.break_ice([self.index[0], self.index[1]+1])
                else:
                    if not self.coll_up():
                        self.move_up()
                    else:
                        self.break_ice([self.index[0], self.index[1]-1])

            elif type(path) is list:
                if self.index[0]-path[1][0] < 0:
                    self.move_right()
                elif self.index[0]-path[1][0] > 0:
                    self.move_left()
                elif self.index[1]-path[1][1] < 0:
                    self.move_down()
                else:
                    self.move_up()

    def radius_player_detection(self): # Returns boolean based on Condition
        return abs(self.player.index[0]-self.index[0]) <= 5 and abs(self.player.index[1]-self.index[1]) <= 5

    def animate(self):
        self.current_time = pg.time.get_ticks()

        if self.moving and self.current_time - self.delay_anim > 70:
            self.delay_anim = self.current_time
            self.index_anim = (self.index_anim + 1) % len(self.anim_down)
            if self.direction == "down":
                self.surface = self.anim_down[self.index_anim]
            elif self.direction == "left":
                self.surface = self.anim_left[self.index_anim]
            elif self.direction == "right":
                self.surface = self.anim_right[self.index_anim]
            elif self.direction == "up":
                self.surface = self.anim_up[self.index_anim]
                    
    def update(self):
        self.current_time = pg.time.get_ticks()
        self.player_grid = self.player.player_grid
        if not self.delaying:
            self.move(); self.animate()
        elif self.current_time - self.delayed > 600:
            self.delaying = False
        self.screen.blit(self.surface, self.rect)
        if self.radius_player_detection():
            if not self.detect_counter:
                self.spot_sound.play()
                self.detect_counter = 1
            if self.current_time - self.delay > 250:
                self.delay = self.current_time
                self.showing = not self.showing
            if self.showing:
                self.screen.blit(self.exclamation_point, self.rect.topleft)
        else:
            self.detect_counter = 0