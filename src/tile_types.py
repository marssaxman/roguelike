from typing import Tuple
import numpy as np  # type: ignore
from functools import cache

import graphics
import color

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", np.bool),  # True if this tile can be walked over.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dt), # Graphics for when  the tile is in view
    ]
)

def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)

@cache
def wall(char_id):
    return new_tile(
        walkable=False,
        transparent=False,
        dark=(char_id, (95, 95, 127), color.black),
        light=(char_id, color.white, color.black),
    )

@cache
def door(char_id):
    return new_tile(
        walkable=True,
        transparent=False,
        dark=(char_id, (95, 95, 127), color.black),
        light=(char_id, color.white, color.black),
    )

@cache
def floor(char_id):
    return new_tile(
        walkable=True,
        transparent=True,
        dark=(char_id, (95, 95, 127), color.black),
        light=(char_id, color.white, color.black),
    )

# Shroud represents tiles which have not yet been explored
SHROUD = np.array((ord(" "), color.white, color.black), dtype=graphic_dt)

# Map initialization value used prior to style painting
DEFAULT = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), (127, 127, 127), (50, 50, 150)),
    light=(ord("#"), color.white, (200, 180, 50)),
)

exit_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(graphics.STAIRS_UP, (0, 0, 100), (50, 50, 150)),
    light=(graphics.STAIRS_UP, color.white, (200, 180, 50)),
)

entry_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(graphics.STAIRS_DOWN, (0, 0, 100), (50, 50, 150)),
    light=(graphics.STAIRS_DOWN, color.white, (200, 180, 50)),
)

