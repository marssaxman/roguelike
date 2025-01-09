# Given an array of map tiles, generate an array of character codes.
# We'll use box-drawing characters to show the direction of wall connections.

import numpy as np
from dataclasses import dataclass
from typing import Any

from .basemap import Tile


@dataclass
class Palette:
    void: Any
    floor: Any
    door: Any
    door_H: Any
    door_V: Any
    wall: Any
    wall_B: Any
    wall_R: Any
    wall_RB: Any
    wall_A: Any
    wall_AB: Any
    wall_AR: Any
    wall_ARB: Any
    wall_L: Any
    wall_LB: Any
    wall_LR: Any
    wall_LRB: Any
    wall_LA: Any
    wall_LAB: Any
    wall_LAR: Any
    wall_LARB: Any
    debug: Any


def place_door(grid, x, y, palette: Palette):
    # If there are walls above and below, return a vertical door.
    # If there are walls left and right, return a horizontal door.
    # Otherwise - this should never happen - return a plus sign.
    if y > 0 and (y+1) < grid.shape[1]:
        if grid[x, y-1] == Tile.WALL and grid[x, y+1] == Tile.WALL:
            return palette.door_V
    if x > 0 and (x+1) < grid.shape[0]:
        if grid[x-1, y] == Tile.WALL and grid[x+1, y] == Tile.WALL:
            return palette.door_H
    return palette.door


def place_wall(grid, x: np.uint, y:np.uint, palette: Palette):
    wall_left = x > 0 and grid[x-1, y] == Tile.WALL
    wall_above = y > 0 and grid[x, y-1] == Tile.WALL
    wall_right = (x+1) < grid.shape[0] and grid[x+1, y] == Tile.WALL
    wall_below = (y+1) < grid.shape[1] and grid[x, y+1] == Tile.WALL
    glyphs = [             # L A R B
        palette.wall,      # . . . .
        palette.wall_B,    # . . . X
        palette.wall_R,    # . . X .
        palette.wall_RB,   # . . X X
        palette.wall_A,    # . X . .
        palette.wall_AB,   # . X . X
        palette.wall_AR,   # . X X .
        palette.wall_ARB,  # . X X X
        palette.wall_L,    # X . . .
        palette.wall_LB,   # X . . X
        palette.wall_LR,   # X . X .
        palette.wall_LRB,  # X . X X
        palette.wall_LA,   # X X . .
        palette.wall_LAB,  # X X . X
        palette.wall_LAR,  # X X X .
        palette.wall_LARB, # X X X X
    ]
    index = 0
    index += 8 if wall_left else 0
    index += 4 if wall_above else 0
    index += 2 if wall_right else 0
    index += 1 if wall_below else 0
    return glyphs[index]


def tiles(src, dest, palette: Palette):
    assert len(src.shape) == 2 and len(dest.shape) == 2
    assert dest.shape[0] >= src.shape[0] and dest.shape[1] >= src.shape[1]
    for x, y in np.ndindex(src.shape):
        src_val = src[x, y]
        dest_val = palette.void
        if src_val == Tile.VOID:
            dest_val = palette.void
        elif src_val == Tile.FLOOR:
            dest_val = palette.floor
        elif src_val == Tile.DOOR:
            dest_val = place_door(src, x, y, palette)
        elif src_val == Tile.WALL:
            dest_val = place_wall(src, x, y, palette)
        elif src_val == Tile.DEBUG:
            dest_val = palette.debug
        dest[x, y] = dest_val

