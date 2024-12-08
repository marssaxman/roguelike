
import tcod

# Basic multilingual plane private use area: 6400 code points
PUA = 0xE000

_next_codepoint = PUA
def _alloc():
    global _next_codepoint
    ret = _next_codepoint
    _next_codepoint += 1
    return ret

PLAYER = _alloc()
RAT = _alloc()
ORC = _alloc()
TROLL = _alloc()

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

    player_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Characters/Player0.png", 8, 15, range(8*15)
    )
    tileset.set_tile(PLAYER, player_tiles.get_tile(0))

    rodent_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Characters/Rodent0.png", 8, 4, range(8*4)
    )
    tileset.set_tile(RAT, rodent_tiles.get_tile(9))

    humanoid_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Characters/Humanoid0.png", 8, 27, range(8*17)
    )
    tileset.set_tile(TROLL, humanoid_tiles.get_tile(0))
    tileset.set_tile(ORC, humanoid_tiles.get_tile(64))

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

