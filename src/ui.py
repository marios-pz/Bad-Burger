import pygame as pg
import src.animation as animation
from .utils import *


class UI:
    def __init__(self, screen, fruit, fps: int):
        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()
        self.fruit_class = fruit
        self.time_left: int = 0
        self.fps: int = fps
        self.clock_animation: animation.Animation = animation.Animation(
            544, 6, [load_alpha(f"data/assets/clock/clock{i+1}.png") for i in range(8)], 3
        )

        self.font_: pg.font.Font = pg.font.Font(None, 25)
        self.text_rendered = self.font_.render("Get all the : ", True, (255, 255, 255))
        self.txt_rd_rect = self.text_rendered.get_rect(centerx=(self.w//3))

    def reset(self, time_for_level):
        self.time_left: int = time_for_level

    def tick(self):
        self.time_left -= (1/self.fps) if self.time_left > 0 else 0

    def get_time(self):
        if self.time_left > 0:
            return f"""{
                int(self.time_left // 60) if len(str(int(self.time_left // 60))) == 2 else f"0{int(self.time_left // 60)}"
            }:{
                int(self.time_left - self.time_left // 60 * 60) if len(str(int(self.time_left - self.time_left // 60 * 60))) == 2 else f"0{int(self.time_left - self.time_left // 60 * 60)}"
            }"""

    def update(self):

        pg.draw.rect(self.screen, (0, 0, 0), [self.txt_rd_rect.x, self.txt_rd_rect.y, self.txt_rd_rect.width+self.fruit_class.current_fruit.image.get_width(), 32])
        self.screen.blit(self.text_rendered, self.txt_rd_rect)
        self.screen.blit(self.fruit_class.current_fruit.image, self.txt_rd_rect.topright)