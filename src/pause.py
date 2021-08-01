import pygame as pg
import src.ratatouille as ratatouille
from src.utils import *


class Pause:

    def __init__(self, screen):

        self.screen = screen
        self.w = screen.get_width()
        self.h = screen.get_height()
        self.clock = pg.time.Clock()

        self.running = True
        self.response = None

        self.bg = resizex(load_alpha("data/assets/credits-background-no-burger.png"), 4)
        self.bg_rect = self.bg.get_rect(center=(self.w // 2, self.h // 2))

        self.button_image = resize(load_alpha("data/assets/button.png"), (120, 35))
        self.buttons_hover_image = resize(load_alpha("data/assets/button_hover.png"), (120, 35))

        self.buttons = ratatouille.init(self.screen)
        self.buttons.new_special_button(
            (self.w//2 - self.button_image.get_width()//2, self.h//2), self.button_image, self.buttons_hover_image,
            (self.button_image.get_width(), self.button_image.get_height()),
            self.set_response, ("resume", )
        )
        self.buttons.new_special_button(
            (self.w//2 - self.button_image.get_width()//2, self.h//2+40), self.button_image, self.buttons_hover_image,
            (self.button_image.get_width(), self.button_image.get_height()),
            self.set_response, ("quit", )
        )

        self.font = pg.font.Font("data/fonts/Minecraft.ttf", 25)
        self.texts = [self.font.render("resume", True, (0, 0, 0)), self.font.render("quit", True, (0, 0, 0))]

        self.opacity_layer = pg.Surface(self.screen.get_size())
        self.opacity_layer.set_alpha(180)

    def set_response(self, response):
        self.response = response

    def event_handler(self, game):
        for event in pg.event.get():
            self.buttons.handle_events(event)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.response = "resume"
            if event.type == pg.QUIT:
                game.__quit__()

    def update(self):

        self.screen.blit(self.bg, self.bg_rect)
        label = self.font.render("GAME PAUSED", True, (0, 0, 0))
        self.screen.blit(label, (self.w//2 - label.get_width()//2, 200))

        self.buttons.update()

        for i, button in enumerate(self.buttons.buttons):
            label = self.texts[i]
            label_rect = label.get_rect(center=button.rect.center)
            self.screen.blit(label, label_rect)

        pg.display.update()

    def run(self, game, fps):
        self.running = True
        self.response = None
        while self.running:
            self.clock.tick(fps)
            self.event_handler(game)
            self.update()

            if self.response is not None:
                self.running = False
                return self.response
