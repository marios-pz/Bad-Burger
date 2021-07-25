import pygame as p


class Player:
    def __init__(self, grid_pos, size, screen):
        self.surface = p.Surface((size, size))
        self.surface.fill((255,0,0))
        self.rect = self.surface.get_rect(topleft= p.Vector2(grid_pos[5].rect.x, grid_pos[5].rect.y))
        self.screen = screen

    def handle_events(self, e):
        if e.type == p.KEYDOWN:
            if e.key == p.K_w:
                self.rect[1] -= 32
            elif e.key == p.K_s:
                self.rect[1] += 32
            if e.key == p.K_d:
                self.rect[0] += 32
            elif e.key == p.K_a:
                self.rect[0] -= 32

    def update(self):
        self.screen.blit(self.surface, self.rect)
