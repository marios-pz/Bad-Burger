import math
import pygame
from src.utils import *
from src.ratatouille import framework
from src.settings import *
import time


class Menu:
    def __init__(self, screen: pygame.surface.Surface, clock: pygame.time.Clock):
        self.screen: pygame.surface.Surface = screen
        self.W: int = WIDTH
        self.H: int = HEIGHT
        self.running: bool = True
        self.font_60: pygame.font.Font = pygame.font.Font(None, 60)
        self.font_50: pygame.font.Font = pygame.font.Font(None, 50)
        self.font_40: pygame.font.Font = pygame.font.Font(None, 40)
        self.clock: pygame.time.Clock = clock

        # -------------------------- BUTTONS ---------------------------- #
        self.buttons: framework.FrameWork = framework.init(self.screen)
        self.buttons.new_special_button((5, 5), load_alpha("data/assets/button.png"), load_alpha("data/assets/button.png"), (100, 50), lambda: quit(-1))
        # self.buttons.new_button(
        #     (3, 3),
        #     pygame.font.Font(None, 50),
        #     "quit",
        #     (0, 0, 0),
        #     (0, 0, 0),
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     (100, 50),
        #     15,
        #     lambda: quit(-1)
        # )

    def draw(self):
        self.screen.fill((255, 100, 50))

        label = self.font_60.render("Bad Burger", True, (0, 0, 0))
        self.screen.blit(label, (self.W/2 - label.get_width()/2, (self.H/2 - label.get_height()/2) + math.sin(time.time() * 5) * 5 - 25))

        label = self.font_60.render("press enter to start", True, (0, 0, 0))
        self.screen.blit(label, (self.W/2 - label.get_width()/2, (self.H - label.get_height() - 150)))

        self.buttons.update()
        label = self.font_50.render("quit", True, (0, 0, 0))
        self.screen.blit(label, ((5 + 100/2 - label.get_width()/2), (5 + 50/2 - label.get_height()/2)))

        pygame.display.update()

    def event_handler(self):
        for event in pygame.event.get():
            self.buttons.handle_events(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(-1)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.running = False

    def run(self, fps):
        while self.running:
            self.clock.tick(fps)
            self.draw()
            self.event_handler()

