# unicode definitions
SPACE = 0x0020
PLUS_SIGN = 0x002B
FULL_STOP = 0x002E
BULLET_OPERATOR = 0x2219
MIDDLE_DOT = 0x00B7
BOX_DRAWINGS_LIGHT_TRIPLE_DASH_VERTICAL = 0x2506
BOX_DRAWINGS_LIGHT_QUADRUPLE_DASH_HORIZONTAL = 0x2508
BOX_DRAWINGS_DOUBLE_HORIZONTAL = 0x2550
BOX_DRAWINGS_DOUBLE_VERTICAL = 0x2551
BOX_DRAWINGS_DOUBLE_DOWN_RIGHT = 0x2554
BOX_DRAWINGS_DOUBLE_DOWN_LEFT = 0x2557
BOX_DRAWINGS_DOUBLE_UP_RIGHT = 0x255A
BOX_DRAWINGS_DOUBLE_UP_LEFT = 0x255D
BOX_DRAWINGS_VERTICAL_SINGLE_RIGHT_DOUBLE = 0x255E
BOX_DRAWINGS_DOUBLE_VERTICAL_RIGHT = 0x2560
BOX_DRAWINGS_VERTICAL_SINGLE_LEFT_DOUBLE = 0x2561
BOX_DRAWINGS_DOUBLE_VERTICAL_LEFT = 0x2563
BOX_DRAWINGS_DOUBLE_DOWN_HORIZONTAL = 0x2566
BOX_DRAWINGS_DOWN_DOUBLE_HORIZONTAL_SINGLE = 0x2565
BOX_DRAWINGS_UP_DOUBLE_HORIZONTAL_SINGLE = 0x2568
BOX_DRAWINGS_DOUBLE_UP_HORIZONTAL = 0x2569
BOX_DRAWINGS_DOUBLE_VERTICAL_HORIZONTAL = 0x256C
WHITE_SQUARE_CONTAINING_BLACK_SMALL_SQUARE = 0x25A3


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
