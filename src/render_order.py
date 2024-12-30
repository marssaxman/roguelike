from enum import auto, Enum


class RenderOrder(Enum):
    LAST = auto()
    CORPSE = auto()
    FIXTURE = auto()
    ITEM = auto()
    ACTOR = auto()

