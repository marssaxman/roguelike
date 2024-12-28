
import tcod
from components import appearance
from dataclasses import dataclass
from functools import cache
import numpy as np

"""
Load the graphic tiles we will use from the files in the assets directory.
Allocate a private-use codepoint for each graphic.
Create appearances which govern the use and animation of these graphics.

The main program must call `load_into`, passing in the tcod tileset. This will
load all the graphics into the tileset under the allocated codepoints.

Published codepoints are names in ALL_CAPS. Appearance objects are published
using lower_case names.
"""

# Basic multilingual plane private use area: 6400 code points
PUA_BEGIN = 0xE000
PUA_END = 0xF8FF

_next_codepoint = PUA_BEGIN
def _alloc():
    global _next_codepoint
    ret = _next_codepoint
    _next_codepoint += 1
    # in future, switch from the BMP PUA to the plane 15 PUA
    assert _next_codepoint <= PUA_END
    return ret

def _alloc_pair():
    return _alloc(), _alloc()

def _alloc_actor():
    # inner pairs are the left and right directionals
    # outer pair represents 0/1 animation frames
    return _alloc_pair(), _alloc_pair()


class TileGroup:
    """Group of tile codes related by LARB proximity."""
    def __init__(self):
        self._codes = [_alloc() for _ in range(16)]

    def index(
        self,
        *,
        left: bool=False,
        above: bool=False,
        right: bool=False,
        below: bool=False
    ):
        index = 0
        index += 8 if left else 0
        index += 4 if above else 0
        index += 2 if right else 0
        index += 1 if below else 0
        return index

    def pick(self, **kwargs):
        return self._codes[self.index(**kwargs)]


class FloorTiles(TileGroup):
    def load(self, tileset, floorpng, start):
        """
        Load a group of floor tiles from the DawnLike set.
        floorpng is "Floor.png" loaded as a tileset.
        start is an offset identifying the tile group.
        """
        offsets = [5, 3, 25, 0, 45, 24, 42, 21, 27, 2, 26, 1, 44, 23, 43, 22]
        for i in range(16):
            tile = floorpng.get_tile(start + offsets[i])
            tileset.set_tile(self._codes[i], tile)


class WallTiles(TileGroup):
    def load(self, tileset, wallpng, start):
        """Load a group of wall tiles from the DawnLike set.
        wallpng is "Wall.png" loaded as a tileset.
        start is an offset in the tileset identifying the tile group.
        """
        offsets = [21, 20, 1, 0, 20, 20, 40, 23, 1, 2, 1, 4, 42, 25, 44, 24]
        for i in range(16):
            tile = wallpng.get_tile(start + offsets[i])
            tileset.set_tile(self._codes[i], tile)

    def flip_red_and_blue(self, tileset):
        """
        Recolor all of these tiles by swapping the red and blue channels.
        This is useful because DawnLike only includes one set of brick tiles,
        which are all cool-toned. We'd like warmer-toned brick options.
        """
        for code in self._codes:
            old = tileset.get_tile(code)
            new = old[:, :, [2,1,0,3]]
            tileset.set_tile(code, new)


def _actor_appearance(quad):
    # Using an actor quad returned by _alloc_actor(), create an Appearance
    return appearance.Looped((
        appearance.Directional(
            left=appearance.Static(char=quad[0][0], color=(255, 255, 255)),
            right=appearance.Static(char=quad[0][1], color=(255, 255, 255)),
        ),
        appearance.Directional(
            left=appearance.Static(char=quad[1][0], color=(255, 255, 255)),
            right=appearance.Static(char=quad[1][1], color=(255, 255, 255)),
        ),
    ))


# We have to store the codepoints we allocated, instead of just passing them
# directly in to the appearance constructor, so we can load the relevant
# graphic tiles in later.
_PLAYER = _alloc_actor()
player = _actor_appearance(_PLAYER)

_RAT = _alloc_actor()
rat = _actor_appearance(_RAT)

_ORC = _alloc_actor()
orc = _actor_appearance(_ORC)

_TROLL = _alloc_actor()
troll = _actor_appearance(_TROLL)


# The rest of these are just codepoints.
CORPSE = _alloc()

DOOR_H = _alloc()
DOOR_V = _alloc()
DOOR = DOOR_H

FLOOR_STONE = [FloorTiles() for _ in range(4)]
FLOOR_WOOD = [FloorTiles() for _ in range(4)]
FLOORS = FLOOR_STONE + FLOOR_WOOD
WALL_BRICK = [WallTiles() for _ in range(8)]
WALL_ROCK = [WallTiles() for _ in range(8)]
WALLS = WALL_BRICK + WALL_ROCK

STAIRS_UP = _alloc()
STAIRS_DOWN = _alloc()

POTION = _alloc()
SCROLL = _alloc()

@cache
def composite(below: int, above: int):
    """Layer one tile on another to create a new tile."""
    global _tileset
    below_tile = _tileset.get_tile(below)
    above_tile = _tileset.get_tile(above)
    # Extract the RGB channels
    srcRGB = above_tile[...,:3]
    dstRGB = below_tile[...,:3]
    # Extract the alpha channels and normalise to range 0..1
    srcA = above_tile[...,3]/255.0
    dstA = below_tile[...,3]/255.0
    # Work out resultant alpha channel
    outA = srcA + dstA*(1-srcA)
    # Work out resultant RGB
    outRGB = (srcRGB*srcA[...,np.newaxis] + dstRGB*dstA[...,np.newaxis]*(1-srcA[...,np.newaxis])) / outA[...,np.newaxis]
    # Merge RGB and alpha (scaled back up to 0..255) back into single image
    outRGBA = np.dstack((outRGB,outA*255)).astype(np.uint8)
    # Allocate a new codepoint and store the new tile image
    out_code = _alloc()
    _tileset.set_tile(out_code, outRGBA)
    return out_code

@cache
def adjoin(left: int, right: int):
    """Combine the left half of one tile with the right half of another."""
    global _tileset
    left_tile = _tileset.get_tile(left)
    right_tile = _tileset.get_tile(right)
    assert left_tile.shape == right_tile.shape
    outRGBA = np.zeros_like(left_tile)
    half_width = left_tile.shape[0] // 2
    outRGBA[::,:half_width,...] = left_tile[::,:half_width,...]
    outRGBA[::,half_width:,...] = right_tile[::,half_width:,...]
    out_code = _alloc()
    _tileset.set_tile(out_code, outRGBA)
    return out_code

def _set_mirrored(tileset, left_right, image):
    left, right = left_right
    tileset.set_tile(left, image)
    tileset.set_tile(right, image[...,::-1,:])

def load_into(tileset):
    """Load all the graphics we might use and assign them codepoints."""
    global _tileset
    _tileset = tileset

    door_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Objects/Door0.png", 8, 6, range(48)
    )
    tileset.set_tile(DOOR_H, door_tiles.get_tile(0))
    tileset.set_tile(DOOR_V, door_tiles.get_tile(1))

    floor_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Objects/Floor.png", 21, 39, range(819)
    )
    FLOOR_STONE[0].load(tileset, floor_tiles, 63)
    FLOOR_STONE[1].load(tileset, floor_tiles, 126)
    FLOOR_STONE[2].load(tileset, floor_tiles, 189)
    FLOOR_STONE[3].load(tileset, floor_tiles, 252)
    FLOOR_WOOD[0].load(tileset, floor_tiles, 322)
    FLOOR_WOOD[1].load(tileset, floor_tiles, 385)
    FLOOR_WOOD[2].load(tileset, floor_tiles, 448)
    FLOOR_WOOD[3].load(tileset, floor_tiles, 511)

    wall_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Objects/Wall.png", (320//16), (816//16), range(1020)
    )
    WALL_BRICK[0].load(tileset, wall_tiles, 60)
    WALL_BRICK[1].load(tileset, wall_tiles, 120)
    WALL_BRICK[2].load(tileset, wall_tiles, 180)
    WALL_BRICK[3].load(tileset, wall_tiles, 240)
    # The second set of brick tiles are the same as the first, color-swapped.
    WALL_BRICK[4].load(tileset, wall_tiles, 60)
    WALL_BRICK[4].flip_red_and_blue(tileset)
    WALL_BRICK[5].load(tileset, wall_tiles, 120)
    WALL_BRICK[5].flip_red_and_blue(tileset)
    WALL_BRICK[6].load(tileset, wall_tiles, 180)
    WALL_BRICK[6].flip_red_and_blue(tileset)
    WALL_BRICK[7].load(tileset, wall_tiles, 240)
    WALL_BRICK[7].flip_red_and_blue(tileset)
    WALL_ROCK[0].load(tileset, wall_tiles, 307)
    WALL_ROCK[1].load(tileset, wall_tiles, 367)
    WALL_ROCK[2].load(tileset, wall_tiles, 427)
    WALL_ROCK[3].load(tileset, wall_tiles, 487)
    WALL_ROCK[4].load(tileset, wall_tiles, 314)
    WALL_ROCK[5].load(tileset, wall_tiles, 374)
    WALL_ROCK[6].load(tileset, wall_tiles, 434)
    WALL_ROCK[7].load(tileset, wall_tiles, 494)

    player0_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Characters/Player0.png", 8, 15, range(8*15)
    )
    _set_mirrored(tileset, _PLAYER[0], player0_tiles.get_tile(0))
    player1_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Characters/Player1.png", 8, 15, range(8*15)
    )
    _set_mirrored(tileset, _PLAYER[1], player1_tiles.get_tile(0))


    rodent0_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Characters/Rodent0.png", 8, 4, range(8*4)
    )
    _set_mirrored(tileset, _RAT[0], rodent0_tiles.get_tile(9))
    rodent1_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Characters/Rodent1.png", 8, 4, range(8*4)
    )
    _set_mirrored(tileset, _RAT[1], rodent1_tiles.get_tile(9))

    humanoid0_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Characters/Humanoid0.png", 8, 27, range(8*17)
    )
    humanoid1_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Characters/Humanoid1.png", 8, 27, range(8*17)
    )
    _set_mirrored(tileset, _TROLL[0], humanoid0_tiles.get_tile(8))
    _set_mirrored(tileset, _TROLL[1], humanoid1_tiles.get_tile(8))
    _set_mirrored(tileset, _ORC[0], humanoid0_tiles.get_tile(64))
    _set_mirrored(tileset, _ORC[1], humanoid1_tiles.get_tile(64))

    potion_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Items/Potion.png", (128//16), (80//16), range(40)
    )
    tileset.set_tile(POTION, potion_tiles.get_tile(0))

    scroll_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Items/Scroll.png", 8, 6, range(8*6)
    )
    tileset.set_tile(SCROLL, scroll_tiles.get_tile(0))

    redjack = tcod.tileset.load_tilesheet(
        "assets/Redjack17.png", 16, 16, range(16*16)
    )
    tileset.set_tile(CORPSE, redjack.get_tile((16*15)+13))
    tileset.set_tile(STAIRS_UP, redjack.get_tile((16*3)+12))
    tileset.set_tile(STAIRS_DOWN, redjack.get_tile((16*3)+14))

