# Build a map, composed of tiles.

import numpy as np
from enum import Enum

class Tile(Enum):
    VOID = 0,
    WALL = 1,
    FLOOR = 2,
    DOOR = 3


# Create and manipulate a base map for a game level.
# All mutation happens through calls to the builder.
# Returned objects are either copied or immutable.
class Builder:
    def __init__(self, width: np.uint, height: np.uint):
        self.map = np.full((width, height), Tile.VOID, dtype=Tile)

    # Array-like accessors
    @property
    def shape(self):
        return self.map.shape

    @property
    def width(self):
        return self.map.shape[0]

    @property
    def height(self):
        return self.map.shape[1]


    # Mutators
    def place_floor(self, x, y, room_id):
        assert self.map[x, y] == Tile.VOID
        self.map[x, y] = Tile.FLOOR if room_id else Tile.VOID

    def place_horz_wall(self, x, y, above_id, below_id):
        assert self.map[x, y] == Tile.VOID
        self.map[x, y] = Tile.WALL

    def place_vert_wall(self, x, y, left_id, right_id):
        assert self.map[x, y] == Tile.VOID
        self.map[x, y] = Tile.WALL

    def place_pillar(self, x, y):
        assert self.map[x, y] == Tile.VOID
        self.map[x, y] = Tile.WALL


    # Retrieve finished copy of contents
    def get_tiles(self):
        return np.copy(self.map)


