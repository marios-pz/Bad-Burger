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


def reset_settings():
    data = {
        "WIDTH": 640,
        "HEIGHT": 480,
        "FPS": 30,
        "credits": [
            "credits",
            "programing:",
            "emc235 | fkS | Mario | hk",
            "art:",
            "Mario | hk",
            "music:",
            "Mario | hk | fkS"
        ],
        "play_music": True,
        "play_sfx": True
    }

    write_json("src/settings", data)
