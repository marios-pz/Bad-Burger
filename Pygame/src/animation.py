import pygame
from itertools import cycle
from typing import List


class Animation:
    def __init__(self, x: int, y: int, images: List[pygame.surface.Surface], frames_per_image: int=5):
        self.x: int = x
        self.y: int = y
        self.images: cycle = cycle(images)
        self.frames_per_image: int = frames_per_image
        self.current_image: pygame.surface.Surface = next(self.images)
        self.time: int = 0

    def animate(self) -> None:
        """
        it cycles throw the images
        :return: None
        """
        if self.time >= self.frames_per_image:
            self.current_image = next(self.images)
            self.time = 0
        self.time += 1

    def update(self, screen: pygame.surface.Surface) -> None:
        """
        it draws the animation to the screen
        :param screen: pygame.surface.Surface
        :return: None
        """
        screen.blit(self.current_image, (self.x, self.y))
