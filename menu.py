import math
import pygame
from src.settings import *
import time


class Menu:
    def __init__(self, screen: pygame.surface.Surface, clock: pygame.time.Clock):
        self.screen: pygame.surface.Surface = screen
        self.W: int = WIDTH
        self.H: int = HEIGHT
        self.running: bool = True
        self.font: pygame.font.Font = pygame.font.Font(None, 60)
        self.clock: pygame.time.Clock = clock

    def draw(self) -> None:
        self.screen.fill((255, 100, 50))

        label = self.font.render("Bad Burger", True, (0, 0, 0))
        self.screen.blit(label, (self.W/2 - label.get_width()/2, (self.H/2 - label.get_height()/2) + math.sin(time.time() * 5) * 5 - 25))

        label = self.font.render("press enter to start", True, (0, 0, 0))
        self.screen.blit(label, (self.W/2 - label.get_width()/2, (self.H - label.get_height() - 150)))

        pygame.display.update()

    def event_handler(self) -> None:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                print(True)
                pygame.quit()
                quit(-1)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.running = False

    def run(self) -> None:
        while self.running:
            self.clock.tick(FPS)
            self.draw()
            self.event_handler()

