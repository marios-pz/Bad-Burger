import pygame as p


class Player:
    def __init__(self, x , y, size, screen):
        self.x, self.y, self.screen = x, y, screen
        self.surface = p.Surface((size, size))
        self.surface.fill((255,0,0))
        self.rect = self.surface.get_rect(topleft= p.Vector2(x,y))

    def handle_events(self, e, ground_tile):
            if e.type == p.KEYDOWN:
                if e.key == p.K_w:
                    print('W')
                elif e.key == p.K_s:
                    print('S')
                if e.key == p.K_d:
                    print('D')
                elif e.key == p.K_a:
                    print('A')

    def update(self):
        print(self.rect)
        self.screen.blit(self.surface, self.rect)
