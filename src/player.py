import pygame as p
from src.tiles import ColliderTiles as CT
import copy
from os import listdir
from src.utils import *


class Player:
    def __init__(self, tile_map, fruits, screen):

        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()
        self.tile_map, self.TLS_X, self.TLS_Y, self.TILE_SIZE = tile_map, tile_map.TLS_X, tile_map.TLS_Y, tile_map.TILE_SIZE
        self.fruits = fruits

        # image
        self.surface = resize(load_alpha("data/assets/walk_left/walk_left1.png"), (32, 32))

        self.player_grid = []
        "self.read_map(self.tile_map.current_map_collider)"
        self.index = [1, 1]
        self.enemy_grp = []

        # rect
        self.rect = self.surface.get_rect(topleft=p.Vector2(self.index[0]*self.TLS_X, self.index[1]*self.TLS_Y))

        self.victory = None
        self.moving = False
        self.direction = "right"
        self.velocity = 5

        self.ordered_spell = False
        self.casting_spell = False

        self.current_time = p.time.get_ticks()
        self.began_casting_spell = 0
        self.delay_anim = 0

        self.moving_anim_left = [load_alpha(f"data/assets/walk_left/{file}") for file in listdir("data/assets/walk_left")]
        self.moving_anim_left = [resize(img, (32, 32)) for img in self.moving_anim_left]
        self.index_anim = 0
        
        self.moving_anim_down = [load_alpha(f"data/assets/walk_down/{file}") for file in listdir("data/assets/walk_down")]
        self.moving_anim_down = [resize(img, (32, 32)) for img in self.moving_anim_down]

        self.moving_anim_up = [load_alpha(f"data/assets/walk_up/{file}") for file in listdir("data/assets/walk_up")]
        self.moving_anim_up = [resize(img, (32, 32)) for img in self.moving_anim_up]

        self.moving_anim_right = [p.transform.flip(img, True, False) for img in self.moving_anim_left]

        self.idle_left = [load_alpha(f"data/assets/idle_left/{file}") for file in listdir("data/assets/idle_left")]
        self.idle_up = [load_alpha(f"data/assets/idle_up/{file}") for file in listdir("data/assets/idle_up")]
        self.idle_down = [load_alpha(f"data/assets/idle_down/{file}") for file in listdir("data/assets/idle_down")]
        self.idle_right = [p.transform.flip(img, True, False) for img in self.idle_left]

        self.kick_animation = [load_alpha(f"data/assets/attack/{file}") for file in listdir("data/assets/attack")]

        self.right_power = [load_alpha(f"data/assets/ability_side/{file}") for file in listdir("data/assets/ability_side")]
        self.left_power = [p.transform.flip(img, True, False) for img in self.right_power]

        self.down_power = [load_alpha(f"data/assets/power_down/{file}") for file in listdir("data/assets/power_down")]
        self.destroying = False

        self.dying_anim = [load_alpha(f"data/assets/player_dying/{file}") for file in listdir("data/assets/player_dying")]
    
        self.winning_anim = [load_alpha(f"data/assets/winning/{file}") for file in listdir("data/assets/winning")]

        self.cooldown = True
        self.delay_cd = self.duration = self.score = 0
        self.cd_direction = self.direction

        self.dying = False

    def eat_fruit(self, ui):
        if self.fruits.grid[self.index[1]][self.index[0]] is not None:
            self.score += self.fruits.grid[self.index[1]][self.index[0]].score *(1 if ui.get_time() else 0.5)
            self.fruits.grid[self.index[1]][self.index[0]] = None

    def init_level(self, level):
        self.victory = None
        self.dying = False
        self.score = 0
        self.index = copy.copy(level.begin_player_pos)
        self.rect = self.surface.get_rect(topleft=p.Vector2(self.index[0]*self.TLS_X, self.index[1]*self.TLS_Y))
        self.read_map(level.path_map)

    def read_map(self, name):
        with open(name, "r") as f: datas = f.readlines()
        self.player_grid = [[1 if col == '1' or col == '2' or col == '3' else 0 for col in row.strip().split()] for row in datas]
        
    def handle_events(self, event):
        # have to fix this for the ordered spell
        """if self.ordered_spell and not self.moving and not self.casting_spell:
            self.ordered_spell = False
            return self.cast_spell()"""

        if event.type == p.KEYDOWN:
            if event.key == p.K_SPACE:
                if not self.moving and not self.casting_spell and not self.cooldown and not self.dying:
                    return self.cast_spell()    
                else:
                    self.ordered_spell = True

    def cast_spell(self):

        if self.direction == "down":
            if self.index[1]+1 > len(self.player_grid)-1:
                return
            next_cell = [self.index[0], self.index[1]+1]
        elif self.direction == "up":
            if self.index[1] - 1 < 1:
                return
            next_cell = [self.index[0], self.index[1]-1]
        elif self.direction == "right":
            if self.index[0] + 1 > len(self.player_grid[self.index[1]])-1:
                return
            next_cell = [self.index[0]+1, self.index[1]]
        elif self.direction == "left":
            if self.index[0] - 1 < 1:
                return
            next_cell = [self.index[0]-1, self.index[1]]

        is_ice = self.check_ice_block(next_cell)
        self.casting_spell = True
        self.began_casting_spell = p.time.get_ticks()
        self.destroying = is_ice[0] # Where output 1 is True and 0 False
        return self.spell_ice(next_cell, self.destroying)


    def reset_ice_blocks(self, indexes: list):
        for index in indexes:
            self.player_grid[index[1]][index[0]] = 0

    def spell_ice(self, first_cell, destruct):
        indexes = []
        is_available = self.check_ice_block(first_cell) if destruct else self.is_blank(first_cell)
        count = 0
        while is_available[0]:
            if destruct:
                is_available[1].destruct(count, first_cell)
            else:
                indexes.append((copy.copy(first_cell), copy.copy(count)))
                self.player_grid[first_cell[1]][first_cell[0]] = 1

            if self.direction == "down":
                if first_cell[1] + 1 < len(self.player_grid):
                    first_cell[1] += 1 
                else:
                    break
            elif self.direction == "up":
                if first_cell[1] - 1 >= 0:
                    first_cell[1] -= 1
                else:
                    break
            elif self.direction == "right":
                if first_cell[0] + 1 < len(self.player_grid[first_cell[1]]):
                    first_cell[0] += 1
                else:
                    break
            elif self.direction == "left":
                if first_cell[0] - 1 >= 0:
                    first_cell[0] -= 1
                else:
                    break

            if destruct:
                is_available = self.check_ice_block(first_cell)
            else:
                
                is_available = self.is_blank(first_cell)

            print(first_cell, end=",")
            count += 1
        print("end")

        self.cooldown = True
        self.delay_cd = pg.time.get_ticks() + count * 100
        self.cd_direction = self.direction
        if destruct:
            self.duration = 500
        else:
            self.duration = 100
        return indexes if not destruct else None

    def check_ice_block(self, index: tuple[int, int]):
        if type(self.tile_map.collider_tiles[index[1]][index[0]]) is CT.IceBlock:
            return True, self.tile_map.collider_tiles[index[1]][index[0]]
        return False, None

    def is_blank(self, indexes):
        for enemy in self.enemy_grp:
            if enemy.index == indexes:
                return (False, None)
        return (True, None) if self.player_grid[indexes[1]][indexes[0]] == 0 else (False, None)

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

    def manage_animation(self, dt):
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

    def animate(self):
        self.current_time = p.time.get_ticks()

        if self.current_time - self.delay_anim > 75:
            self.delay_anim = self.current_time
            self.index_anim = (self.index_anim + 1) % len(self.moving_anim_right)

            if self.direction == "right":
                self.surface = self.moving_anim_right[self.index_anim]

            elif self.direction == "down":
                self.surface = self.moving_anim_down[self.index_anim]

            elif self.direction == "up":
                self.surface = self.moving_anim_up[self.index_anim]

            elif self.direction == "left":
                self.surface = self.moving_anim_left[self.index_anim]
            
            self.rect = self.surface.get_rect(center=self.rect.center)

    def animate_idle(self):
        self.current_time = p.time.get_ticks()

        if self.current_time - self.delay_anim > 150:
                self.delay_anim = self.current_time
                self.index_anim = (self.index_anim + 1) % len(self.idle_right)

                if self.direction == "right":
                    self.surface = self.idle_right[self.index_anim]

                elif self.direction == "down":
                    self.surface = self.idle_down[self.index_anim]

                elif self.direction == "up":
                    self.surface = self.idle_up[self.index_anim]

                elif self.direction == "left":
                    self.surface = self.idle_left[self.index_anim]
                
                self.rect = self.surface.get_rect(center=self.rect.center)

    def animate_attack(self):
        self.current_time = p.time.get_ticks()

        if self.current_time - self.delay_anim > 500 / 8:
            self.delay_anim = self.current_time

            if self.destroying:

                self.index_anim = (self.index_anim + 1) % len(self.kick_animation)
                self.surface = self.kick_animation[self.index_anim]
                self.rect = self.surface.get_rect(center=self.rect.center)
            else:
                self.index_anim = (self.index_anim + 1) % len(self.left_power)

                if self.direction == "down":
                    self.surface = self.down_power[self.index_anim]
                elif self.direction == "left":
                    self.surface = self.left_power[self.index_anim]
                elif self.direction == "right":
                    self.surface = self.right_power[self.index_anim]
                elif self.direction == "up":
                    self.surface = self.down_power[self.index_anim]
                
                self.rect = self.surface.get_rect(center=self.rect.center)

    def update(self, dt, enemy_grp, ui):
        # update current time
        self.current_time = p.time.get_ticks()
        # update enemy group
        self.enemy_grp = enemy_grp

        # animate the player while moving to another tile
        if self.moving:
            
            self.animate()

            self.manage_animation(dt)

        elif self.casting_spell:

            if self.current_time - self.began_casting_spell > 500:
                self.casting_spell = False
            self.animate_attack()

        else:
            if not self.dying and not self.victory:
                self.animate_idle()

        self.eat_fruit(ui)
        # draw the player
        self.screen.blit(self.surface, self.rect)

        if self.cooldown and self.cd_direction != self.direction or self.current_time - self.delay_cd > self.duration:
            self.cooldown = False

        if self.victory:
            if self.current_time - self.delay_anim > 75:
                self.delay_anim = self.current_time
                self.index_anim = (self.index_anim + 1) % len(self.winning_anim)
                self.surface = self.winning_anim[self.index_anim]
                self.rect = self.surface.get_rect(center=self.rect.center)

        if self.dying:
            if self.current_time - self.delay_anim > 75:
                if self.index_anim < len(self.dying_anim)-1:
                    self.index_anim += 1
                self.delay_anim = self.current_time
                self.surface = self.dying_anim[self.index_anim]
                self.rect = self.surface.get_rect(center=self.rect.center)

        if not self.casting_spell and not self.dying and self.victory is None:
            # get keys pressed
            pressed = p.key.get_pressed()
            if pressed[p.K_LEFT]:
                self.animate()
                self.move_left()
            elif pressed[p.K_RIGHT]:
                self.animate()
                self.move_right()
            elif pressed[p.K_DOWN]:
                self.animate()
                self.move_down()
            elif pressed[p.K_UP]:
                self.animate()
                self.move_up()

