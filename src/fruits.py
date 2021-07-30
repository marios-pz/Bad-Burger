from copy import copy
from typing import List
import pprint
import pygame
from pygame.display import update
from src.utils import *


class Fruits:
    class Banana:
        def __init__(self, screen: pygame.surface.Surface, size: tuple[int, int], coordinates: tuple[int, int]):
            self.screen: pygame.surface.Surface = screen
            self.w: int = screen.get_width()
            self.h: int = screen.get_height()

            self.image: pygame.surface.Surface = resize(load_alpha("data/assets/fruits/banana.png"), size)

            self.rect = self.image.get_rect(topleft=coordinates)

        def update(self):
            self.screen.blit(self.image, self.rect)

    class Cherry:
        def __init__(self, screen: pygame.surface.Surface, size: tuple[int, int], coordinates: tuple[int, int]):
            self.screen: pygame.surface.Surface = screen
            self.w: int = screen.get_width()
            self.h: int = screen.get_height()

            self.image: pygame.surface.Surface = resize(load_alpha("data/assets/fruits/cherry.png"), size)

            self.rect = self.image.get_rect(topleft=coordinates)

        def update(self):
            self.screen.blit(self.image, self.rect)

    class Lemon:
        def __init__(self, screen: pygame.surface.Surface, size: tuple[int, int], coordinates: tuple[int, int]):
            self.screen: pygame.surface.Surface = screen
            self.w: int = screen.get_width()
            self.h: int = screen.get_height()

            self.image: pygame.surface.Surface = resize(load_alpha("data/assets/fruits/lemon.png"), size)

            self.rect = self.image.get_rect(topleft=coordinates)

        def update(self):
            self.screen.blit(self.image, self.rect)

    class Grape:
        def __init__(self, screen: pygame.surface.Surface, size: tuple[int, int], coordinates: tuple[int, int]):
            self.screen: pygame.surface.Surface = screen
            self.w: int = screen.get_width()
            self.h: int = screen.get_height()

            self.image: pygame.surface.Surface = resize(load_alpha("data/assets/fruits/grape.png"), size)

            self.rect = self.image.get_rect(topleft=coordinates)

        def update(self):
            self.screen.blit(self.image, self.rect)


class FruitMap:
    def __init__(self, screen: pygame.surface.Surface, TILE_SIZE: tuple[int, int], FRUIT_SIZE: tuple[int, int]):
        self.screen: pygame.surface.Surface = screen

        self.TILE_SIZE: tuple[int, int] = TILE_SIZE
        self.TILE_W: int = TILE_SIZE[0]
        self.TILE_H: int = TILE_SIZE[1]
        self.FRUIT_SIZE: tuple[int, int] = FRUIT_SIZE
        self.FRUIT_W: int = FRUIT_SIZE[0]
        self.FRUIT_H: int = FRUIT_SIZE[1]

        self.grid: List[list] = []

        self.keys = {
            "1": Fruits.Banana,
            "2": Fruits.Cherry,
            "3": Fruits.Lemon,
            "4": Fruits.Grape
        }

        self.paths = []
        self.state = 0
        self.current_fruit = []
        
    def init_level(self, level):
        self.state = 0
        self.paths = [path for path in level.path_fruits]
        self.read_map(self.paths[self.state])
        self.get_fruits()

    def get_fruits(self):
        self.current_fruit = []
        for path in self.paths:
            with open(path, "r") as f:
                datas = f.read()
            for key in self.keys:
                if key in datas:
                    self.current_fruit.append(copy(self.keys[key](self.screen, self.FRUIT_SIZE, (0,0)).image))

    def read_map(self, path):
        self.grid = []
        with open(path, "r") as f:
            data = f.readlines()

            for ir, row in enumerate(data):

                row = row.strip()
                row = row.replace(" ", "")

                self.grid.append([])

                for ic, fruit in enumerate(row):
                    if fruit in self.keys:
                        self.grid[ir].append(self.keys[fruit](self.screen, self.FRUIT_SIZE, (
                            ic*self.TILE_W + (self.TILE_W - self.FRUIT_W)//2,
                            ir*self.TILE_H + (self.TILE_H - self.FRUIT_H)//2
                        )))
                    else:
                        self.grid[ir].append(None)

    def init_state(self):
        if self.state >= len(self.paths)-1:
            return "victory"
        else:
            self.state += 1
            self.read_map(self.paths[self.state])
            return "initialized next state"

    def update(self):
        updated = False
        for _r in self.grid:
            for fruit in _r:
                if fruit is not None:
                    updated = True
                    fruit.update()

        if not updated:
            
            init_ = self.init_state()
            if init_ == "victory":
                print(init_)
                return "victory"
