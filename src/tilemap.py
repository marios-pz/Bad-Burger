import pygame as pg
import random
import src.tiles as tiles


class TileMap:

    def __init__(self, screen, tile_size):
        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()

        # list to store all the ground tiles
        self.ground_tiles = []

        # list to store all the collider tiles
        self.collider_tiles = []

        # dict to assign a key to a tile
        self.keys = {
            "0": tiles.GroundTiles.Grass,
            "1": tiles.GroundTiles.Rock
        }

        self.keys_collider = {
            "1": tiles.ColliderTiles.IceBlock,
            "2": tiles.ColliderTiles.Furnace,
            "3": tiles.ColliderTiles.Table
        }

        # TILE SIZE
        self.TILE_SIZE = (tile_size, tile_size)
        self.TLS_X = self.TILE_SIZE[0]  # tile size x shortcut
        self.TLS_Y = self.TILE_SIZE[1]  # tile size y shortcut

        self.read_map("data/map.txt", False)
        """self.read_map("map_collider", True)"""

        self.current_map_collider = "map_collider"

    def init_level(self, level):
        self.current_map_collider = level.path
        self.read_map(self.current_map_collider, True)

    def read_map(self, name, collider):
        
        if collider:
            self.collider_tiles = []
        else:
            self.ground_tiles = []

        # get the doc
        with open(name, "r") as f:
            datas = f.readlines()  # read the content

        # loop through it
        for index_r, row in enumerate(datas):
            # remove \n in the line
            row = row.strip()
            if collider:
                row_ = []
            for index_c, col in enumerate(row):
                # check if the key exists
                if not collider:
                    if col in self.keys:
                        # add to the ground tile storage the assignated tile to the key, with the size and the coordinates
                        self.ground_tiles.append(self.keys[col](self.screen, self.TILE_SIZE, (index_c*self.TLS_X, index_r*self.TLS_Y)))
                else:
                    if col in self.keys_collider:
                        row_.append(self.keys_collider[col](self.screen, self.TILE_SIZE, (index_c*self.TLS_X, index_r*self.TLS_Y), False, 0))
                    else:
                        row_.append(None)
            if collider:
                self.collider_tiles.append(row_)

    def add_ices(self, indexes: list):
        for index in indexes:
            self.collider_tiles[index[0][1]][index[0][0]] = self.keys_collider["1"](self.screen, self.TILE_SIZE, (index[0][0]*self.TLS_X, index[0][1]*self.TLS_Y), True, index[1]*100)

    def update_ground(self):
        # blit all the tiles on the screen
        for ground_tile in self.ground_tiles:
            ground_tile.update()

    def update_colliders(self): 
        
        to_remove = []
        # blit all colliders
        for index_r, colliders in enumerate(self.collider_tiles):
            for index_c, collider in enumerate(colliders):
                if collider is not None:
                    kill = collider.update()
                    if kill[0] == "kill":
                        to_remove.append((collider, kill[1], (index_c, index_r)))

        for collider in to_remove:
            self.collider_tiles[collider[2][1]][collider[2][0]] = None
        return [tr[1] for tr in to_remove] if len([tr[1] for tr in to_remove]) > 0 else None
