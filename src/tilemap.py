import pygame as pg
import src.tiles as tiles


class TileMap:

    def __init__(self, screen):
        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()

        self.ground_tiles = []

        self.keys = {
            "0": tiles.GroundTiles.Grass,
            "1": tiles.GroundTiles.Rock
        }
        self.tile_size = (32, 32)
        self.tl_s_x = self.tile_size[0]
        self.tl_s_y = self.tile_size[1]

        self.read_map("map")

    def read_map(self, name):

        with open(f"data/{name}.txt", "r") as f:
            datas = f.readlines()

        for index_r, row in enumerate(datas):
            row = row.strip()
            for index_c, col in enumerate(row):
                self.ground_tiles.append(self.keys[col](self.screen, self.tile_size, (index_c*self.tl_s_x, index_r*self.tl_s_y)))

    def update(self):
        
        for ground_tile in self.ground_tiles:
            ground_tile.update()