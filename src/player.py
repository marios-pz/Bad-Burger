import pygame as p


class Player:
    def __init__(self, tile_map, size, screen):

        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()
        self.tile_map, self.TLS_X, self.TLS_Y, self.TILE_SIZE = tile_map, tile_map.TLS_X, tile_map.TLS_Y, tile_map.TILE_SIZE

        # image
        self.surface = p.Surface((size, size))
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

    def handle_events(self, e):
        # don't delete this method, we might need it later
        pass

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

