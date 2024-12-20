
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


@dataclass
class FloorTiles:
    """Group of codepoints representing a single floor style."""
    UpperLeft: int
    UpperCenter: int
    UpperRight: int
    UpperVert: int
    Solo: int
    MiddleLeft: int
    MiddleCenter: int
    MiddleRight: int
    MiddleVert: int
    HorzLeft: int
    HorzCenter: int
    HorzRight: int
    LowerLeft: int
    LowerCenter: int
    LowerRight: int
    LowerVert: int

    @staticmethod
    def alloc():
        return FloorTiles(
            UpperLeft=_alloc(),
            UpperCenter=_alloc(),
            UpperRight=_alloc(),
            UpperVert=_alloc(),
            Solo=_alloc(),
            MiddleLeft=_alloc(),
            MiddleCenter=_alloc(),
            MiddleRight=_alloc(),
            MiddleVert=_alloc(),
            HorzLeft=_alloc(),
            HorzCenter=_alloc(),
            HorzRight=_alloc(),
            LowerLeft=_alloc(),
            LowerCenter=_alloc(),
            LowerRight=_alloc(),
            LowerVert=_alloc(),
        )

    def load(self, tileset, floorpng, start):
        tileset.set_tile(self.UpperLeft, floorpng.get_tile(start + 0))
        tileset.set_tile(self.UpperCenter, floorpng.get_tile(start + 1))
        tileset.set_tile(self.UpperRight, floorpng.get_tile(start + 2))
        tileset.set_tile(self.UpperVert, floorpng.get_tile(start + 3))
        tileset.set_tile(self.Solo, floorpng.get_tile(start + 5))
        tileset.set_tile(self.MiddleLeft, floorpng.get_tile(start + 21))
        tileset.set_tile(self.MiddleCenter, floorpng.get_tile(start + 22))
        tileset.set_tile(self.MiddleRight, floorpng.get_tile(start + 23))
        tileset.set_tile(self.MiddleVert, floorpng.get_tile(start + 24))
        tileset.set_tile(self.HorzLeft, floorpng.get_tile(start + 25))
        tileset.set_tile(self.HorzCenter, floorpng.get_tile(start + 26))
        tileset.set_tile(self.HorzRight, floorpng.get_tile(start + 27))
        tileset.set_tile(self.LowerLeft, floorpng.get_tile(start + 42))
        tileset.set_tile(self.LowerCenter, floorpng.get_tile(start + 43))
        tileset.set_tile(self.LowerRight, floorpng.get_tile(start + 44))
        tileset.set_tile(self.LowerVert, floorpng.get_tile(start + 45))

    def larb(self):
        # Return an array of codes in LARB bitfield order.
        return [                # L A R B
            self.Solo,          # . . . .
            self.UpperVert,     # . . . B
            self.HorzLeft,      # . . R .
            self.UpperLeft,     # . . R B
            self.LowerVert,     # . A . .
            self.MiddleVert,    # . A . B
            self.LowerLeft,     # . A R .
            self.MiddleLeft,    # . A R B
            self.HorzRight,     # L . . .
            self.UpperRight,    # L . . B
            self.HorzCenter,    # L . R .
            self.UpperCenter,   # L . R B
            self.LowerRight,    # L A . .
            self.MiddleRight,   # L A . B
            self.LowerCenter,   # L A R .
            self.MiddleCenter,  # L A R B
        ]


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

_RAT = _alloc_pair(), _alloc_pair()
rat = _actor_appearance(_RAT)

_ORC = _alloc_pair(), _alloc_pair()
orc = _actor_appearance(_ORC)

_TROLL = _alloc_pair(), _alloc_pair()
troll = _actor_appearance(_TROLL)


# The rest of these are just codepoints.
CORPSE = _alloc()

COLUMN = _alloc()
WALL = _alloc()
WALL_L = _alloc()
WALL_A = _alloc()
WALL_R = _alloc()
WALL_B = _alloc()
WALL_LR = _alloc()
WALL_AB = _alloc()
WALL_RB = _alloc()
WALL_LB = _alloc()
WALL_AR = _alloc()
WALL_LA = _alloc()
WALL_ARB = _alloc()
WALL_LAB = _alloc()
WALL_LRB = _alloc()
WALL_LAR = _alloc()
WALL_LARB = _alloc()
DOOR_H = _alloc()
DOOR_V = _alloc()
DOOR = DOOR_H

FLOOR_STONE = [
    FloorTiles.alloc(),
    FloorTiles.alloc(),
    FloorTiles.alloc(),
    FloorTiles.alloc()
]
FLOOR_WOOD = [
    FloorTiles.alloc(),
    FloorTiles.alloc(),
    FloorTiles.alloc(),
    FloorTiles.alloc()
]
FLOORS = FLOOR_STONE + FLOOR_WOOD

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


def _set_mirrored(tileset, left_right, image):
    left, right = left_right
    tileset.set_tile(left, image)
    tileset.set_tile(right, image[...,::-1,:])

def load_into(tileset):
    """Load all the graphics we might use and assign them codepoints."""
    global _tileset
    _tileset = tileset
    # load some graphics for the walls
    wall_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Objects/Wall.png", (320//16), (816//16), range(1020)
    )
    # 20 tiles in a row, 51 rows
    # Wall tiles exist in a 6x3 cluster with 1 space between columns
    # Clusters exist in a 4-high group (6x12 tiles) of color variants
    # We'll use the brick cluster in row 1
    # Within a cluster, tiles are located like thus:
    # RB    LR    LB    #       LRB
    # AB    A           ARB     LARB    LAB
    # AR          LA            LAR
    # (B = AB, L = AL, R=AR)
    tileset.set_tile(WALL, wall_tiles.get_tile(63))
    tileset.set_tile(WALL_L, wall_tiles.get_tile(61))
    tileset.set_tile(WALL_A, wall_tiles.get_tile(81))
    tileset.set_tile(WALL_R, wall_tiles.get_tile(61))
    tileset.set_tile(WALL_B, wall_tiles.get_tile(80))
    tileset.set_tile(WALL_LR, wall_tiles.get_tile(61))
    tileset.set_tile(WALL_AB, wall_tiles.get_tile(80))
    tileset.set_tile(WALL_RB, wall_tiles.get_tile(60))
    tileset.set_tile(WALL_LB, wall_tiles.get_tile(62))
    tileset.set_tile(WALL_AR, wall_tiles.get_tile(100))
    tileset.set_tile(WALL_LA, wall_tiles.get_tile(102))
    tileset.set_tile(WALL_ARB, wall_tiles.get_tile(83))
    tileset.set_tile(WALL_LAB, wall_tiles.get_tile(85))
    tileset.set_tile(WALL_LRB, wall_tiles.get_tile(64))
    tileset.set_tile(WALL_LAR, wall_tiles.get_tile(104))
    tileset.set_tile(WALL_LARB, wall_tiles.get_tile(84))

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

