import pygame as pg
from math import floor


def load(path: str):
    return pg.image.load(path).convert()

def load_alpha(path: str):
    return pg.image.load(path).convert_alpha()

def resize(image: pg.Surface, new_size: tuple[int, int]):
    return pg.transform.smoothscale(image, new_size)

def resize_ratio(image: pg.Surface, new_size: tuple[int, int]):
    ratio = new_size[0]/image.get_width()
    return pg.transform.scale(image, (floor(image.get_width()*ratio), floor(image.get_height()*ratio)))