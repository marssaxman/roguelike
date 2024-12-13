
import tcod
from components import appearance

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
PUA = 0xE000

_next_codepoint = PUA
def _alloc():
    global _next_codepoint
    ret = _next_codepoint
    _next_codepoint += 1
    return ret

def _alloc_pair():
    return _alloc(), _alloc()

def _alloc_actor():
    # inner pairs are the left and right directionals
    # outer pair represents 0/1 animation frames
    return _alloc_pair(), _alloc_pair()

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

STAIRS_UP = _alloc()
STAIRS_DOWN = _alloc()

POTION = _alloc()
SCROLL = _alloc()

def _set_mirrored(tileset, left_right, image):
    left, right = left_right
    tileset.set_tile(left, image)
    tileset.set_tile(right, image[...,::-1,:])


def load_into(tileset):
    """Load all the graphics we might use and assign them codepoints."""
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
    _set_mirrored(tileset, _TROLL[0], humanoid0_tiles.get_tile(0))
    _set_mirrored(tileset, _TROLL[1], humanoid1_tiles.get_tile(0))
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

