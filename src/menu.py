import math
import pygame
from .ratatouille import *
from .utils import *
import time


class Menu:
    def __init__(self, screen: pygame.surface.Surface, clock: pygame.time.Clock):
        self.settings = get_json("src/settings")

        # ----------------------- SCREEN -------------------------------- #
        self.screen: pygame.surface.Surface = screen
        self.W: int = self.settings["WIDTH"]
        self.H: int = self.settings["HEIGHT"]

        # ---------------------- VARIABLES ------------------------------ #
        self.logo: pygame.surface.Surface = load_alpha("data/assets/logo.png")
        self.music_on: pygame.surface.Surface = load_alpha("data/assets/music_on.png")
        self.music_off: pygame.surface.Surface = load_alpha("data/assets/music_off.png")
        self.sfx_on: pygame.surface.Surface = load_alpha("data/assets/sfx_on.png")
        self.sfx_off: pygame.surface.Surface = load_alpha("data/assets/sfx_off.png")
        self.running: bool = True
        self.font_60: pygame.font.Font = pygame.font.Font(None, 60)
        self.font_50: pygame.font.Font = pygame.font.Font(None, 50)
        self.font_40: pygame.font.Font = pygame.font.Font(None, 40)
        self.clock: pygame.time.Clock = clock
        self.credits: bool = False
        self.clicked_first_button: bool = False
        self.last_time: float = time.time()
        self.dt: float = None

        # -------------------------- BUTTONS ---------------------------- #
        self.button_image = load_alpha("data/assets/button.png")

        self.buttons: FrameWork = init(self.screen)
        self.buttons.new_special_button((self.W // 2 - 100 // 2, self.H // 2 - 50 // 2 + 80), self.button_image, self.button_image, (100, 40), self.stop_running)  # play
        self.buttons.new_special_button((self.W // 2 - 160 // 2, self.H // 2 - 50 // 2 + 125), self.button_image, self.button_image, (160, 40))  # settings
        self.buttons.new_special_button((self.W // 2 - 140 // 2, self.H // 2 - 50 // 2 + 170), self.button_image, self.button_image, (140, 40), self.switch_credits)  # credits
        self.buttons.new_special_button((self.W // 2 - 100 // 2, self.H // 2 - 50 // 2 + 215), self.button_image, self.button_image, (100, 40),  self.quit)  # quit

        self.credits_back: SpecialButton = SpecialButton((5, 5), self.button_image, self.button_image, (100, 40), self.switch_credits)
        self.start_menu: SpecialButton = SpecialButton((self.W // 2 - 170 // 2, self.H // 2 - 50 // 2 + 80), self.button_image, self.button_image, (170, 40), self.toggle_clicked_first_button)

        self.sound_buttons: FrameWork = init(self.screen)
        self.sound_buttons.new_special_button((self.W - 35, 5), self.music_on, self.music_on, (32, 32), self.toggle_sounds)
        self.sound_buttons.new_special_button((self.W - 67, 4), self.sfx_on, self.sfx_on, (32, 32), self.toggle_sfx)

    def toggle_clicked_first_button(self):
        self.clicked_first_button = not self.clicked_first_button

    @staticmethod
    def quit():
        reset_settings()
        pygame.quit()
        quit(-1)

    def toggle_sounds(self):
        self.settings["play_music"]: bool = not self.settings["play_music"]
        if self.settings["play_music"]:
            self.sound_buttons.buttons[0].image = pg.transform.smoothscale(self.music_on, (32, 32))
            self.sound_buttons.buttons[0].image_hover = pg.transform.smoothscale(self.music_on, (32, 32))
        else:
            self.sound_buttons.buttons[0].image = pg.transform.smoothscale(self.music_off, (32, 32))
            self.sound_buttons.buttons[0].image_hover = pg.transform.smoothscale(self.music_off, (32, 32))

    def toggle_sfx(self):
        self.settings["play_sfx"]: bool = not self.settings["play_sfx"]
        if self.settings["play_sfx"]:
            self.sound_buttons.buttons[1].image = pg.transform.smoothscale(self.sfx_on, (32, 32))
            self.sound_buttons.buttons[1].image_hover = pg.transform.smoothscale(self.sfx_on, (32, 32))
        else:
            self.sound_buttons.buttons[1].image = pg.transform.smoothscale(self.sfx_off, (32, 32))
            self.sound_buttons.buttons[1].image_hover = pg.transform.smoothscale(self.sfx_off, (32, 32))

    def stop_running(self):
        self.running = False

    def switch_credits(self):
        self.credits = not self.credits

    def draw(self):
        self.screen.fill((255, 100, 50))

        self.screen.blit(self.logo, (self.W//2 - self.logo.get_width()//2, (20 + math.sin(time.time() * 5) * 5 - 25)*self.dt))
        self.sound_buttons.update()

        if self.clicked_first_button:
            self.buttons.update()

            label = self.font_40.render("play", True, (0, 0, 0))
            self.screen.blit(label, (self.W // 2 - label.get_width() // 2, self.H // 2 - label.get_height() // 2 + 75))

            label = self.font_40.render("settings", True, (0, 0, 0))
            self.screen.blit(label, (self.W // 2 - label.get_width() // 2, self.H // 2 - label.get_height() // 2 + 120))

            label = self.font_40.render("credits", True, (0, 0, 0))
            self.screen.blit(label, (self.W // 2 - label.get_width() // 2, self.H // 2 - label.get_height() // 2 + 165))

            label = self.font_40.render("quit", True, (0, 0, 0))
            self.screen.blit(label, (self.W // 2 - label.get_width() // 2, self.H // 2 - label.get_height() // 2 + 210))

            if self.credits:
                self.screen.blit(resize_ratio(load_alpha("data/assets/credits-background.png"), (540, 380)), (50, 50))
                self.credits_back.update(self.screen)

                label = self.font_40.render("back", True, (0, 0, 0))
                self.screen.blit(label, (5 + 100 // 2 - label.get_width() // 2, 0 + 50 // 2 - label.get_height() // 2))

                height = self.font_40.get_height()
                for i, text in enumerate(self.settings["credits"]):
                    rendered_text_surface = self.font_40.render(text, True, (0, 0, 0))
                    self.screen.blit(rendered_text_surface, (self.W / 2 - rendered_text_surface.get_width() / 2, 50 + (380 - height * len(self.settings["credits"])) / 2 + (i * height)))

        else:
            self.start_menu.update(self.screen)
            label = self.font_40.render("click to eat", True, (0, 0, 0))
            self.screen.blit(label, (self.W // 2 - label.get_width() // 2, self.H // 2 - label.get_height() // 2 + 75))

        pygame.display.update()

    def event_handler(self):
        for event in pygame.event.get():

            if self.clicked_first_button:
                if self.credits:  # check if the credits are drawn

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.credits_back.handle_click(event.pos)
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.switch_credits()
                else:
                    self.buttons.handle_events(event)

            else:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.start_menu.handle_click(event.pos)

            self.sound_buttons.handle_events(event)
            if event.type == pygame.QUIT:
                reset_settings()
                pygame.quit()
                quit(-1)
 
    def run(self, fps):
        while self.running:
            self.clock.tick(fps)
            self.dt = time.time() - self.last_time
            self.dt *= 60
            self.last_time = time.time()
            self.draw()
            self.event_handler()
        write_json("src/settings", self.settings)
