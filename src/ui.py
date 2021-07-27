import pygame
import src.animation as animation
from .utils import *


class UI:
    def __init__(self, fps: int):
        self.time_left: int = 0
        self.fps: int = fps
        self.clock_animation: animation.Animation = animation.Animation(
            535, 5, [load_alpha(f"data/assets/clock/clock{i+1}.png") for i in range(8)], 3
        )

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
