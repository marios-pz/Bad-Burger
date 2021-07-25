import pygame as p
from src.tiles import ColliderTiles as CT
import copy


class Player:
    def __init__(self, tile_map, screen):

        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()
        self.tile_map, self.TLS_X, self.TLS_Y, self.TILE_SIZE = tile_map, tile_map.TLS_X, tile_map.TLS_Y, tile_map.TILE_SIZE

        # image
        self.surface = p.Surface(tile_map.TILE_SIZE)
        self.surface.fill((255,0,0))

        self.player_grid = []
        self.read_map(self.tile_map.current_map_collider)
        self.index = [0, 0]

        # rect
        self.rect = self.surface.get_rect(topleft= p.Vector2(self.index[0]*self.TLS_X, self.index[1]*self.TLS_Y))

        self.moving = False
        self.direction = "right"
        self.velocity = 6

    def read_map(self, name):

        with open(f"data/{name}.txt", "r") as f:
            datas = f.readlines()

        self.player_grid = []
        for row in datas:
            row = row.strip()
            line = []
            for col in row:
                line.append(0) if col == "0" else line.append(1)
            self.player_grid.append(line)

    def handle_events(self, event):
        if event.type == p.KEYDOWN:
            if event.key == p.K_SPACE:
                return self.cast_spell()    
                    

    def cast_spell(self):
        if self.moving:
            return

        if self.direction == "down":
            if self.index[1]+1 > len(self.player_grid):
                return
            next_cell = [self.index[0], self.index[1]+1]
        elif self.direction == "up":
            if self.index[1] - 1 < 0:
                return
            next_cell = [self.index[0], self.index[1]-1]
        elif self.direction == "right":
            if self.index[0] + 1 > len(self.player_grid[self.index[1]]):
                return
            next_cell = [self.index[0]+1, self.index[1]]
        elif self.direction == "left":
            if self.index[0] - 1 < 0:
                return
            next_cell = [self.index[0]-1, self.index[1]]

        is_ice = self.check_ice_block(next_cell)
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
                print(is_available)


            count += 1

        return indexes if not destruct else None

    def check_ice_block(self, index: tuple[int, int]):
        pos = index[0]*self.TLS_X, index[1]*self.TLS_Y
        pos += p.Vector2(*self.TILE_SIZE)//2

        for tile in self.tile_map.collider_tiles:
            if tile.rect.collidepoint(pos) and type(tile) is CT.IceBlock:
                return True, tile
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
        if id_x + 1 > len(self.player_grid[id_y]) or self.player_grid[id_y][id_x+1] == 1:
            return True
        return False

    def coll_left(self):
        id_x, id_y = self.index  
        if id_x - 1 < 0 or self.player_grid[id_y][id_x-1] == 1:
            return True
        return False

    def coll_up(self):
        id_x, id_y = self.index
        if id_y - 1 < 0 or self.player_grid[id_y-1][id_x] == 1:
            return True
        return False

    def coll_down(self):
        id_x, id_y = self.index
        if id_y + 1 > len(self.player_grid) or self.player_grid[id_y+1][id_x] == 1:
            return True
        return False

    def manage_animation(self):
        if self.direction == "right":
            if self.rect.x + self.velocity >= self.index[0]*self.TLS_X:
                self.moving = False
                self.rect.x += (self.index[0]*self.TLS_X - self.rect.x)
            else:
                self.rect.x += self.velocity
        elif self.direction == "left":
            if self.rect.x - self.velocity <= self.index[0]*self.TLS_X:
                self.moving = False
                self.rect.x -= (self.rect.x - self.index[0]*self.TLS_X )
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
                self.rect.y += ((self.index[1]*self.TLS_Y-self.rect.y))
            else:
                self.rect.y += self.velocity

    def update(self):
        # animate the player while moving to another tile
        if self.moving:
            self.manage_animation()

        # get keys pressed
        pressed = p.key.get_pressed()
        if pressed[p.K_LEFT]:
            self.move_left()
        elif pressed[p.K_RIGHT]:
            self.move_right()
        elif pressed[p.K_DOWN]:
            self.move_down()
        elif pressed[p.K_UP]:
            self.move_up()

        # draw the player
        self.screen.blit(self.surface, self.rect)

