
# Given an array of map tiles, generate an array of character codes.
# We'll use box-drawing characters to show the direction of wall connections.

from basemap import Tile
import numpy as np

SPACE = 32
HASH = 35
PERIOD = 46
PLUS = 43
#HBAR = 45
#VBAR = 124


DOOR_H = 0x2508
DOOR_V = 0x2506
PILLAR = 0x25A3

# box drawing characters, heavy lines
WALL_L = 0x2561
WALL_T = 0x2568
WALL_R = 0x255E
WALL_B = 0x2565
WALL_LR = 0x2550
WALL_TB = 0x2551
WALL_RB = 0x2554
WALL_LB = 0x2557
WALL_TR = 0x255A
WALL_LT = 0x255D
WALL_TRB = 0x2560
WALL_LTB = 0x2563
WALL_LRB = 0x2566
WALL_LTR = 0x2569
WALL_LTRB = 0x256C


# We will look up the appropriate wall character by generating a bit mask
# representing the neighboring top, left, bottom, and right squares: each one
# which contains another wall will have its bit set. We can then sum the
# adjacent items and return the appropriate character.
WALL_GLYPHS = [# L T R B
    PILLAR,    # . . . .
    WALL_B,    # . . . X
    WALL_R,    # . . X .
    WALL_RB,   # . . X X
    WALL_T,    # . X . .
    WALL_TB,   # . X . X
    WALL_TR,   # . X X .
    WALL_TRB,  # . X X X
    WALL_L,    # X . . .
    WALL_LB,   # X . . X
    WALL_LR,   # X . X .
    WALL_LRB,  # X . X X
    WALL_LT,   # X X . .
    WALL_LTB,  # X X . X
    WALL_LTR,  # X X X .
    WALL_LTRB, # X X X X
]


def place_door(grid, x, y):
    # If there are walls above and below, return a vertical door.
    # If there are walls left and right, return a horizontal door.
    # Otherwise - this should never happen - return a plus sign.
    if y > 0 and (y+1) < grid.shape[1]:
        if grid[x, y-1] == Tile.WALL and grid[x, y+1] == Tile.WALL:
            return DOOR_V
    if x > 0 and (x+1) < grid.shape[0]:
        if grid[x-1, y] == Tile.WALL and grid[x+1, y] == Tile.WALL:
            return DOOR_H
    return PLUS


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
    maze = np.full(shape=grid.shape, dtype=np.uint32, fill_value=SPACE)
    for x, y in np.ndindex(maze.shape):
        tile = grid[x, y]
        char = 0
        if tile == Tile.VOID:
            char = SPACE
        elif tile == Tile.FLOOR:
            char = PERIOD
        elif tile == Tile.DOOR:
            char = place_door(grid, x, y)
        elif tile == Tile.WALL:
            char = place_wall(grid, x, y)
        maze[x, y] = char
    return maze

