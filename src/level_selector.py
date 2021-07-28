import pygame
from . import ratatouille
from .utils import *


class LevelSelector:
    def __init__(self, screen: pygame.surface.Surface, settings: dict, clock: pygame.time.Clock, available_levels: int=1,
                 last_level_unlocked: int=1):
        """
        :param screen: pygame.surface.Surface
        :param settings: dict
        :param clock: pygame.time.Clock
        :param available_levels: int
        :param last_level_unlocked: int
        """
        self.settings: dict = settings

        # ------------------ SCREEN VARIABLES --------------------- #
        self.screen: pygame.surface.Surface = screen
        self.W: int = self.settings["WIDTH"]
        self.H: int = self.settings["HEIGHT"]

        # ------------------ VARIABLES ---------------------------- #
        self.running: bool = True
        self.button_size: tuple[int, int] = (40, 40)
        self.font_60: pygame.font.Font = pygame.font.Font(None, 60)
        self.font_50: pygame.font.Font = pygame.font.Font(None, 50)
        self.font_40: pygame.font.Font = pygame.font.Font(None, 40)
        self.clock: pygame.time.Clock = clock
        self.table: pygame.surface.Surface = load_alpha("data/assets/table.png")
        self.level_not_available_scaled: pygame.surface.Surface = resize(load_alpha("data/assets/level_not_available.png"), (35, 45))
        self.background_image = pygame.transform.scale(load_alpha("data/assets/credits-background.png"), (self.W, self.H))
        self.button_image = load_alpha("data/assets/button.png")
        self.button_hover_image = load_alpha("data/assets/button_hover.png")
        self.buttons_unlocked_hovering = [resize(load(f"data/assets/hover_button_animation/hover_unlocked_{i+1}.png"), self.button_size) for i in range(2)]
        self.selected_level: int = None
        self.available_levels: int = available_levels
        self.last_level_unlocked: int = last_level_unlocked
        self.response: any = None
        self.time: int = 0
        self.spacing_per_button = 10
        self.frames_per_sprite: int = 3

        # ------------------- BUTTONS ----------------------------- #
        self.level_buttons: ratatouille.FrameWork = ratatouille.init(self.screen)
        self.load_buttons()

        self.back_button = ratatouille.SpecialButton((self.W//2 - 100//2, self.H - 100), self.button_image, self.button_hover_image, (100, 40), self.back)

    def load_buttons(self):
        x, y = 124, 130  # 140
        for available_level in range(self.available_levels):
            self.level_buttons.new_special_button((x, y), self.button_image, self.button_hover_image if available_level+1 <= self.last_level_unlocked else self.button_image, self.button_size, self._get_level, (available_level+1, ))
            x += self.button_size[0] + self.spacing_per_button
            if x >= 500:
                x = 124
                y += self.button_size[1] + self.spacing_per_button

    @staticmethod
    def __quit__():
        """
        it quits the program
        :return: None
        """
        pygame.quit()
        quit(-1)

    def back(self):
        """
        it sets the response to back so the player can go to the menu
        :return: None
        """
        self.response = "back"

    def _get_level(self, number):
        """
        it sets the response to the number of the level if the number is smaller or equal to the self.last_level_unlocked
        :param number: int
        :return: None
        """
        if number <= self.last_level_unlocked:
            self.selected_level: int = number
            self.response = number

    def draw_level_buttons(self):
        for button in self.level_buttons.buttons:
            if button.rect.collidepoint(pygame.mouse.get_pos()):
                if button.args[0] <= self.last_level_unlocked:
                    button.image_hover = self.buttons_unlocked_hovering[self.time//self.frames_per_sprite]
                    self.time += 1
                    if self.time >= self.frames_per_sprite*2:
                        self.time = 0

        self.level_buttons.update()

    def update(self):
        """
        it draws the level selector on the screen
        :return: None
        """
        self.screen.fill((255, 100, 50))
        # drawing the table background
        for x in range(26):
            for y in range(25):
                self.screen.blit(self.table, (x*32, y*28))
        self.screen.blit(self.background_image, (0, 0))  # drawing the image that the buttons are going to be on
        self.draw_level_buttons()

        # draw "level select" to the screen
        label = self.font_60.render("level select", True, (0, 0, 0))
        self.screen.blit(label, (self.W//2 - label.get_width()//2, 40))

        self.back_button.update(self.screen)  # draw the back button and the text for it
        label = self.font_40.render("back", True, (0, 0, 0))
        self.screen.blit(label, (self.W//2 - label.get_width()//2, self.H - 80 - label.get_height()//2))

        for button in self.level_buttons.buttons:  # draw the numbers of the buttons and if needed the cross to tell the player that those levels aren't unlocked yet
            label = self.font_40.render(str(button.args[0]), True, (0, 0, 0))
            self.screen.blit(label, (button.rect[0] + self.button_size[0]//2 - label.get_width()//2, button.rect[1] + self.button_size[1]//2 - label.get_height()//2))
            if button.args[0] > self.last_level_unlocked:
                self.screen.blit(self.level_not_available_scaled, (
                    button.rect.x + button.rect.w//2 - self.level_not_available_scaled.get_width()//2,
                    button.rect.y + (self.button_size[1] - self.level_not_available_scaled.get_height())
                                                                   )
                                 )

        pygame.display.update()

    def event_handler(self):
        """
        it handles all the events of this class
        :return: None
        """
        for event in pygame.event.get():
            self.level_buttons.handle_events(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.back_button.handle_click(event.pos)
            elif event.type == pygame.QUIT:
                self.__quit__()

    def run(self, fps):
        """
        call this method to run the level selector it will
         automatically set it to running and reset the
          response to None so there will be no infinite loop
        :param fps: int
        :return: None
        """
        self.running = True
        self.response = None
        while self.running:
            self.clock.tick(fps)
            self.update()
            self.event_handler()
            if self.response is not None:
                self.running = False
        return self.response
