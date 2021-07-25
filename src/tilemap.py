import pygame as pg
import src.tiles as tiles


class TileMap:

    def __init__(self, screen):
        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()

        # list to store all the ground tiles
        self.ground_tiles = []

        # dict to assign a key to a tile
        self.keys = {
            "0": tiles.GroundTiles.Grass,
            "1": tiles.GroundTiles.Rock
        }

        # TILE SIZE
        self.TILE_SIZE = (32, 32)
        self.TLS_X = self.TILE_SIZE[0]  # tile size x shortcut
        self.TLS_Y = self.TILE_SIZE[1]  # tile size y shortcut

        self.read_map("map")

    def read_map(self, name):

        # get the doc
        with open(f"data/{name}.txt", "r") as f:
            datas = f.readlines()  # read the content

        # loop through it
        for index_r, row in enumerate(datas):
            # remove \n in the line
            row = row.strip()
            for index_c, col in enumerate(row):
                # add to the ground tile storage the assignated tile to the key, with the size and the coordinates
                self.ground_tiles.append(self.keys[col](self.screen, self.TILE_SIZE, (index_c*self.TLS_X, index_r*self.TLS_Y)))

    def update(self):
        
        # blit all the tiles on the screen
        for ground_tile in self.ground_tiles:
            ground_tile.update()