import pygame as pg
import random


class Enemy1:

    def __init__(self, screen, player, tile_map, fruits, dep_pos, type):

        self.screen = screen

        self.surface = pg.Surface((32, 32))
        self.rect = self.surface.get_rect(topleft=(dep_pos[0] * 32, dep_pos[1] * 32))
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

    def collide_fruits(self):
        for id_r, row in enumerate(self.fruits.grid):
            for id_c, col in enumerate(row):
                if col is not None:
                    if self.index == [id_c, id_r]:
                        self.eat_fruit([id_c, id_r])

    def move(self):
        if self.moving:
            self.manage_animation()
        else:
            if   not self.coll_right() and self.direction == "right":
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

    def update(self):
        self.collide_fruits()
        self.player_grid = self.player.player_grid
        self.move()

        self.screen.blit(self.surface, self.rect)
