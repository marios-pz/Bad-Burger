import pygame as p
from src.tiles import ColliderTiles as CT
import copy
from os import listdir
from src.utils import *


class Player:
    def __init__(self, tile_map, screen):

        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()
        self.tile_map, self.TLS_X, self.TLS_Y, self.TILE_SIZE = tile_map, tile_map.TLS_X, tile_map.TLS_Y, tile_map.TILE_SIZE

        # image
        self.surface = resize(load_alpha("data/assets/walk_left/walk_left1.png"), (32, 32))

        self.player_grid = []
        "self.read_map(self.tile_map.current_map_collider)"
        self.index = [1, 1]

        # rect
        self.rect = self.surface.get_rect(topleft=p.Vector2(self.index[0]*self.TLS_X, self.index[1]*self.TLS_Y))

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

    def init_level(self, level):
        self.index = copy.copy(level.begin_player_pos)
        self.rect = self.surface.get_rect(topleft=p.Vector2(self.index[0]*self.TLS_X, self.index[1]*self.TLS_Y))
        self.read_map(level.path)

    def read_map(self, name):

        with open(name, "r") as f:
            datas = f.readlines()

        '''
        self.player_grid = [  We change to this one if it isn't glitchy

            [0 if col == '0' else 1 for col in row.strip()]          
            for row in datas
        ]
        '''
       
        self.player_grid = []
        for row in datas:
            row = row.strip()
            row = row.replace(" ", "")
            line = []
            print(row)
            for col in row:
                if col == "1" or col == "2" or col == "3":
                    line.append(1)
                else:
                    line.append(0)
            self.player_grid.append(line)
        
    def handle_events(self, event):
        # have to fix this for the ordered spell
        """if self.ordered_spell and not self.moving and not self.casting_spell:
            self.ordered_spell = False
            return self.cast_spell()"""

        if event.type == p.KEYDOWN:
            if event.key == p.K_SPACE:
                if not self.moving and not self.casting_spell:
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

        if is_ice[0]:
            self.spell_ice(next_cell, True)
        else:
            return self.spell_ice(next_cell, False)

    def reset_ice_blocks(self, indexes: list):
        for index in indexes:
            self.player_grid[index[1]][index[0]] = 0

    def spell_ice(self, first_cell, destruct):
        indexes = []
        if destruct:
            is_available = self.check_ice_block(first_cell)
        else:
            is_available = self.is_blank(first_cell)
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
        return indexes if not destruct else None

    def check_ice_block(self, index: tuple[int, int]):
        if type(self.tile_map.collider_tiles[index[1]][index[0]]) is CT.IceBlock:
            return True, self.tile_map.collider_tiles[index[1]][index[0]]
        return False, None

    def is_blank(self, indexes):
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
                    self.rect = self.surface.get_rect(center=self.rect.center)

                elif self.direction == "down":

                    self.surface = self.moving_anim_down[self.index_anim]
                    self.rect = self.surface.get_rect(center=self.rect.center)

                elif self.direction == "up":

                    self.surface = self.moving_anim_up[self.index_anim]
                    self.rect = self.surface.get_rect(center=self.rect.center)

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
                    self.rect = self.surface.get_rect(center=self.rect.center)

                elif self.direction == "down":

                    self.surface = self.idle_down[self.index_anim]
                    self.rect = self.surface.get_rect(center=self.rect.center)

                elif self.direction == "up":

                    self.surface = self.idle_up[self.index_anim]
                    self.rect = self.surface.get_rect(center=self.rect.center)

                elif self.direction == "left":
                    
                    self.surface = self.idle_left[self.index_anim]
                    self.rect = self.surface.get_rect(center=self.rect.center)

    def animate_attack(self):
        self.current_time = p.time.get_ticks()

        if self.current_time - self.delay_anim > 500 / 8:
            self.delay_anim = self.current_time
            self.index_anim = (self.index_anim + 1) % len(self.kick_animation)

            self.surface = self.kick_animation[self.index_anim]
            self.rect = self.surface.get_rect(center=self.rect.center)


    def update(self, dt):
        # update current time
        self.current_time = p.time.get_ticks()

        # animate the player while moving to another tile
        if self.moving:
            
            self.animate()

            self.manage_animation(dt)

        elif self.casting_spell:

            if self.current_time - self.began_casting_spell > 500:
                self.casting_spell = False
                self.direction = "down"

            self.animate_attack()

        else:
            
            self.animate_idle()
            # PUT HERE HIS WAITING ANIMATION

        # draw the player
        self.screen.blit(self.surface, self.rect)

        if not self.casting_spell:
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

        # DEBUG MODE :
        """for index, row in enumerate(self.player_grid):
            for index2, col in enumerate(row):
                if col == 1:
                    pg.draw.rect(self.screen, (255, 0, 0), [index2*32, index*32, 32, 32])"""

