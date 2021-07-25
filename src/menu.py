import math
import pygame
from src.utils import *
from src.ratatouille import framework, spec_button
from src.settings import *
import time


class Menu:
    def __init__(self, screen: pygame.surface.Surface, clock: pygame.time.Clock):
        # ----------------------- SCREEN -------------------------------- #
        self.screen: pygame.surface.Surface = screen
        self.W: int = WIDTH
        self.H: int = HEIGHT

        # ---------------------- VARIABLES ------------------------------ #
        self.running: bool = True
        self.font_60: pygame.font.Font = pygame.font.Font(None, 60)
        self.font_50: pygame.font.Font = pygame.font.Font(None, 50)
        self.font_40: pygame.font.Font = pygame.font.Font(None, 40)
        self.clock: pygame.time.Clock = clock
        self.credits: bool = False

        # -------------------------- BUTTONS ---------------------------- #
        self.button_image = load_alpha("data/assets/button.png")
        self.buttons: framework.FrameWork = framework.init(self.screen)
        self.buttons.new_special_button((WIDTH // 2 - 100 // 2, HEIGHT // 2 - 50 // 2), resize(self.button_image, (100, 50)), resize(self.button_image, (100, 50)), (100, 50), self.stop_running)  # play
        self.buttons.new_special_button((WIDTH // 2 - 160 // 2, HEIGHT // 2 - 50 // 2 + 55), resize(self.button_image, (160, 50)), resize(self.button_image, (160, 50)), (160, 50))  # settings
        self.buttons.new_special_button((WIDTH // 2 - 140 // 2, HEIGHT // 2 - 50 // 2 + 110), resize(self.button_image, (140, 50)), resize(self.button_image, (140, 50)), (140, 50), self.switch_credits)  # credits
        self.buttons.new_special_button((WIDTH // 2 - 100 // 2, HEIGHT // 2 - 50 // 2 + 165), resize(self.button_image, (100, 50)), resize(self.button_image, (100, 50)), (100, 50), lambda: quit(-1))  # quit

        self.credits_back: spec_button.SpecialButton = spec_button.SpecialButton((5, 5), self.button_image, self.button_image, (100, 40), self.switch_credits)

    def stop_running(self):
        """
        used by the play button to stop the menu from running and start the game
        :return: None
        """
        self.running = False

    def switch_credits(self):
        self.credits = not self.credits

    def draw(self):
        self.screen.fill((255, 100, 50))

        label = self.font_60.render("Bad Burger", True, (0, 0, 0))
        self.screen.blit(label, (self.W / 2 - label.get_width() / 2, (self.H / 2 - label.get_height() / 2 - 30) + math.sin(time.time() * 5) * 5 - 25))

        self.buttons.update()

        label = self.font_50.render("play", True, (0, 0, 0))
        self.screen.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2 - label.get_height() // 2))

        label = self.font_50.render("settings", True, (0, 0, 0))
        self.screen.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2 - label.get_height() // 2 + 55))

        label = self.font_50.render("credits", True, (0, 0, 0))
        self.screen.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2 - label.get_height() // 2 + 110))

        label = self.font_50.render("quit", True, (0, 0, 0))
        self.screen.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2 - label.get_height() // 2 + 165))

        if self.credits:
            self.screen.blit(resize_ratio(load_alpha("data/assets/credits-background.png"), (540, 380)), (50, 50))
            self.credits_back.update(self.screen)

            label = self.font_40.render("back", True, (0, 0, 0))
            self.screen.blit(label, (5 + 100 // 2 - label.get_width() // 2, 0 + 50 // 2 - label.get_height() // 2))

            height = self.font_40.get_height()
            for i, text in enumerate(credits):
                rendered_text_surface = self.font_40.render(text, True, (0, 0, 0))
                self.screen.blit(rendered_text_surface, (WIDTH / 2 - rendered_text_surface.get_width() / 2, 50 + (380 - height * len(credits)) / 2 + (i * height)))

        pygame.display.update()

    def event_handler(self):
        for event in pygame.event.get():
            if self.credits:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.credits_back.handle_click(event.pos)
            else:
                self.buttons.handle_events(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(-1)
 
    def run(self, fps):
        while self.running:
            self.clock.tick(fps)
            self.draw()
            self.event_handler()
