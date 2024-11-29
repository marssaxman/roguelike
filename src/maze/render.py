# Given an array of map tiles, generate an array of character codes.
# We'll use box-drawing characters to show the direction of wall connections.

import numpy as np
from dataclasses import dataclass
from typing import Any

from .basemap import Tile
import codepoint as cp

# We will look up the appropriate wall character by generating a bit mask
# representing the neighboring top, left, bottom, and right squares: each one
# which contains another wall will have its bit set. We can then sum the
# adjacent items and return the appropriate character.
WALL_GLYPHS = [# L T R B
    cp.COLUMN,    # . . . .
    cp.WALL_B,    # . . . X
    cp.WALL_R,    # . . X .
    cp.WALL_RB,   # . . X X
    cp.WALL_A,    # . X . .
    cp.WALL_AB,   # . X . X
    cp.WALL_AR,   # . X X .
    cp.WALL_ARB,  # . X X X
    cp.WALL_L,    # X . . .
    cp.WALL_LB,   # X . . X
    cp.WALL_LR,   # X . X .
    cp.WALL_LRB,  # X . X X
    cp.WALL_LA,   # X X . .
    cp.WALL_LAB,  # X X . X
    cp.WALL_LAR,  # X X X .
    cp.WALL_LARB, # X X X X
]


def place_door(grid, x, y):
    # If there are walls above and below, return a vertical door.
    # If there are walls left and right, return a horizontal door.
    # Otherwise - this should never happen - return a plus sign.
    if y > 0 and (y+1) < grid.shape[1]:
        if grid[x, y-1] == Tile.WALL and grid[x, y+1] == Tile.WALL:
            return cp.DOOR_V
    if x > 0 and (x+1) < grid.shape[0]:
        if grid[x-1, y] == Tile.WALL and grid[x+1, y] == Tile.WALL:
            return cp.DOOR_H
    return cp.PLUS_SIGN


def place_wall(grid, x: np.uint, y:np.uint):
    wall_left = x > 0 and grid[x-1, y] == Tile.WALL
    wall_above = y > 0 and grid[x, y-1] == Tile.WALL
    wall_right = (x+1) < grid.shape[0] and grid[x+1, y] == Tile.WALL
    wall_below = (y+1) < grid.shape[1] and grid[x, y+1] == Tile.WALL
    index = 0
    index += 8 if wall_left else 0
    index += 4 if wall_above else 0
    index += 2 if wall_right else 0
    index += 1 if wall_below else 0
    return WALL_GLYPHS[index]


def to_chars(grid):
    maze = np.full(shape=grid.shape, dtype=np.uint32, fill_value=cp.SPACE)
    for x, y in np.ndindex(maze.shape):
        tile = grid[x, y]
        char = 0
        if tile == Tile.VOID:
            char = cp.SPACE
        elif tile == Tile.FLOOR:
            char = cp.FULL_STOP
        elif tile == Tile.DOOR:
            char = place_door(grid, x, y)
        elif tile == Tile.WALL:
            char = place_wall(grid, x, y)
        maze[x, y] = char
    return maze


@dataclass
class Palette:
    void: Any
    floor: Any
    door: Any
    wall: Any

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
            dest_val = palette.door
        elif src_val == Tile.WALL:
            dest_val = palette.wall
        dest[x, y] = dest_val

