import pygame as pg
from src.game import Game


if __name__ == "__main__":

    pg.init()

    game = Game()
    game.run()