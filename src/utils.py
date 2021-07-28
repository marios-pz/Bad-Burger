import pygame as pg
import json
from math import floor


def load(path: str):
    return pg.image.load(path).convert()


def load_alpha(path: str):
    return pg.image.load(path).convert_alpha()


def resize(image: pg.Surface, new_size: tuple[int, int]):
    return pg.transform.smoothscale(image, new_size)


def resize_ratio(image: pg.Surface, new_size: tuple[int, int]):
    ratio = new_size[0] / image.get_width()
    return pg.transform.scale(image, (floor(image.get_width() * ratio), floor(image.get_height() * ratio)))


def resizex(image: pg.surface.Surface, amount: int or float) -> pg.surface.Surface:
    w, h = image.get_width(), image.get_height()
    return pg.transform.scale(image, (w*amount, h*amount))


def wrap_multi_lines(text: str, font: pg.font.Font, max_width: int, antialias: bool=True) -> list:
    finished_lines = [""]

    for word in text.split(" "):
        if font.render(finished_lines[-1] + word, antialias, (0, 0, 0)).get_width() > max_width:
            finished_lines.append(f"""{word}""")
        else:
            finished_lines[-1] += f""" {word}"""
    finished_lines[0] = finished_lines[0][1:]

    return finished_lines


def blit_multiple_lines(x: int, y: int, lines: list, screen: pg.surface.Surface, font: pg.font.Font, centered_x=False,
                        centered_x_pos: int=None, color: tuple[int, int, int]=(0, 0, 0)) -> None:
    """
    it sets-up the text. this method has to be called when the text changes
    :param x: int
    :param y: int
    :param lines: list
    :param screen: pg.surface.Surface
    :param font: pg.font.Font
    :param centered_x: if the text is going to be x-centered
    :param centered_x_pos: the rect that is going to be used if centered_x is True
    :param color:
    :return: None
    """
    if centered_x and not centered_x_pos:
        exit("missing hte center_x_pos")
    height = font.get_height()
    for i, text in enumerate(lines):
        rendered_text_surface = font.render(text, True, color)

        if centered_x:
            screen.blit(rendered_text_surface, (centered_x_pos - rendered_text_surface.get_width()/2, y + (i * height)))

        else:
            screen.blit(rendered_text_surface, (x, y + (i*height)))


def get_json(path: str):
    """
    :param path: the specified file name inside db file.
    :return: dict
    """
    with open(f"{path}.json", "r") as f:
        return json.loads(f.read())


def write_json(path: str, DATA: dict, indent: int = 4):
    """
    :param path: str
    :param DATA: dict
    :param indent: int=4
    """
    with open(f"{path}.json", "w") as f:
        f.truncate(0)
        json.dump(DATA, f, indent=indent)
