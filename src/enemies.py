from copy import copy
import pygame as pg
import random
from statistics import mean


class Enemy1:

    def __init__(self, screen, player, tile_map, fruits, dep_pos, type):
        
        self.screen = screen

        self.surface = pg.Surface((32, 32))
        self.rect = self.surface.get_rect(topleft=(dep_pos[0]*32, dep_pos[1]*32))
        self.index = list(dep_pos)

        self.fruits = fruits
        self.player_grid = player.player_grid
        self.player = player

        self.direction = "right"
        self.moving = False
        self.velocity = 4

        self.TLS_Y = tile_map.TLS_Y
        self.TLS_X = tile_map.TLS_X

        self.target = None
        self.tr_dir_x = None
        self.tr_dir_y = None
        self.nearest = None
        self.nr_id = None
        self.nr_obj = None

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
        if id_x + 1 > len(self.player_grid[id_y])-2 or self.player_grid[id_y][id_x+1] == 1:
            return True
        return False

    def coll_left(self):
        id_x, id_y = self.index  
        if id_x - 1 < 1 or self.player_grid[id_y][id_x-1] == 1:
            return True
        return False

    def coll_up(self):
        id_x, id_y = self.index
        if id_y - 1 < 1 or self.player_grid[id_y-1][id_x] == 1:
            return True
        return False

    def coll_down(self):
        id_x, id_y = self.index
        if id_y + 1 > len(self.player_grid)-2 or self.player_grid[id_y+1][id_x] == 1:
            return True
        return False

    def manage_animation(self):
        if self.direction == "right":
            if self.rect.x + (self.velocity) >= self.index[0]*self.TLS_X:
                self.moving = False
                self.rect.x += (self.index[0]*self.TLS_X - self.rect.x)
            else:
                self.rect.x += self.velocity
        elif self.direction == "left":
            if self.rect.x - self.velocity <= self.index[0]*self.TLS_X:
                self.moving = False
                self.rect.x -= (self.rect.x - self.index[0]*self.TLS_X)
            else:
                self.rect.x -= self.velocity
        elif self.direction == "up":
            if self.rect.y - self.velocity <= self.index[1]*self.TLS_Y:
                self.moving = False
                self.rect.y -= (self.rect.y-self.index[1]*self.TLS_Y)
            else:
                self.rect.y -= self.velocity
        elif self.direction == "down":
            if self.rect.y + self.velocity >= self.index[1]*self.TLS_Y:
                self.moving = False
                self.rect.y += (self.index[1]*self.TLS_Y-self.rect.y)
            else:
                self.rect.y += self.velocity

    def collide_fruits(self):
        for id_r, row in enumerate(self.fruits.grid):
            for id_c, col in enumerate(row):
                if col is not None:
                    if self.index == [id_c, id_r]:
                        self.eat_fruit([id_c, id_r])

    def choose_move(self):
        if self.target is None:
            self.nearest = self.find_nearest()
            self.nr_id = self.nearest[1]
            self.target = self.nearest[0]

        else:
            if self.fruits.grid[self.nr_id[1]][self.nr_id[0]] is None:
                self.target = None
        
        dx = self.index[0]-self.nr_id[0]
        dy = self.index[1]-self.nr_id[1]

        self.tr_dir_x = "left" if dx > 0 else "right"
        self.tr_dir_y = "up" if dy > 0 else "down"

        if dx == 0:
            self.tr_dir_x = None
        
        if dy == 0:
            self.tr_dir_y = None


        if self.tr_dir_x == "left":
            self.move_left()
        elif self.tr_dir_x == "right":
            self.move_right()
        
        if self.tr_dir_y == "up":
            self.move_up()
        elif self.tr_dir_y == "down":
            self.move_down()

    def find_nearest(self):
        cur_min = None
        cur_min_id = [1000, 1000]
        for id_r, row in enumerate(self.fruits.grid):
            for id_c, col in enumerate(row):
                if col is not None and self.player_grid[id_r][id_c] == 0:
                    if mean([abs(id_c-self.index[0]), abs(id_r-self.index[1])]) < mean([abs(cur_min_id[0]-self.index[0]), abs(cur_min_id[1]-self.index[1])]):
                        cur_min = col
                        cur_min_id = [id_c, id_r]
   
        return cur_min, cur_min_id
    

    def update(self):
        self.player_grid = self.player.player_grid
        self.collide_fruits()
        self.choose_move()

        if self.moving:
            self.manage_animation()
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

        nearest = self.find_nearest()
        pg.draw.rect(self.screen, (0, 255, 0), [nearest[1][0]*32, nearest[1][1]*32, 32, 32])

        self.screen.blit(self.surface, self.rect)

