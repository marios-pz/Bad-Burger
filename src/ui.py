import pygame as pg
from pygame import image
import src.animation as animation
from .utils import *
from copy import copy


class UI:
    def __init__(self, screen, fruit, fps: int):
        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()
        self.fruit_class = fruit
        self.time_left: int = 0
        self.fps: int = fps
        self.clock_animation: animation.Animation = animation.Animation(
            544, 6, [load_alpha(f"data/assets/clock/clock{i+1}.png") for i in range(8)], 3
        )

        img = load_alpha("data/assets/frut_background.png")
        self.ui_fruits: pg.Surface = pg.transform.scale(img, (img.get_width()*2, int(img.get_height()*1.2)))
        
        self.ui_fr_rect: pg.Rect = self.ui_fruits.get_rect(centerx=self.w//2, bottom=self.h-5)
        self.images = self.fruit_class.current_fruit
        self.images = [resize(img, (int(img.get_width()*0.8), int(img.get_height()*0.8))) for img in self.images]
        self.rects = [img.get_rect(center=(self.ui_fr_rect.centerx-(len(self.images)//2)*id_, self.ui_fr_rect.centery)) for id_, img in enumerate(self.images)]

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
        
        self.screen.blit(self.ui_fruits, self.ui_fr_rect)

        prev = copy(self.images)
        self.images = self.fruit_class.current_fruit

        if prev != self.images:
            # update images if they change (avoid doing this everytime and adding a func to init fruits)
            self.images = [resize(img, (int(img.get_width()*0.8), int(img.get_height()*0.8))) for img in self.images]
        self.rects = [img.get_rect(center=(self.ui_fr_rect.centerx-(((len(self.images)//2)-id_)*32), self.ui_fr_rect.centery)) for id_, img in enumerate(self.images)]

        for id_, img in enumerate(self.images):
            self.screen.blit(img, self.rects[id_])

        st_rct = self.rects[self.fruit_class.state]
        pg.draw.rect(self.screen, (0, 0, 0), [st_rct.x-2, st_rct.y-2, st_rct.width+4, st_rct.height+4], width=2)
        

        
