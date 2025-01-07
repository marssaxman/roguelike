# Build a map, composed of tiles.

import numpy as np
from enum import Enum
from typing import Dict, Set, Tuple, List, Optional

class Tile(Enum):
    VOID = 0,
    WALL = 1,
    FLOOR = 2,
    DOOR = 3,


class Room:
    """A game region consisting of a contiguous set of floor tiles."""
    """A room with ID 0 represents the void, which cannot contain anything."""
    id: int
    _tiles: Set[Tuple[int, int]]
    _neighbors: Set[int]
    _connections: Set[int]
    def __init__(self, id: int):
        self.id = id
        self._tiles = set()
        self._neighbors = set()
        self._connections = set()

    # Public accessors
    def is_empty(self):
        return 0 == len(self._tiles) if self.id else True

    def tiles(self):
        return frozenset(self._tiles) if self.id else frozenset()

    def neighbor_ids(self):
        return frozenset(self._neighbors) if self.id else frozenset()

    def connection_ids(self):
        return frozenset(self._connections) if self.id else frozenset()

    def is_connected(self):
        return len(self._connections) if self.id else False

    def is_corridor(self):
        if not self.id or not self._tiles:
            return False
        first_x, first_y = next(iter(self._tiles))
        corr_h, corr_v = True, True
        for x, y in self._tiles:
            if x != first_x:
                corr_v = False
            if y != first_y:
                corr_h = False
        if corr_h == corr_v:
            return False
        if len(self._tiles) <= 4:
            return False
        return True

    def random_location(self, rng) -> Tuple[int, int]:
        return rng.choice(list(self._tiles))

    # Internal manipulators for use by Builder
    def _add_tile(self, x, y):
        if self.id == 0:
            return
        self._tiles.add((x, y))

    def _add_neighbor(self, other_id):
        if self.id == 0:
            return
        assert other_id != self.id
        if other_id != 0:
            self._neighbors.add(other_id)

    def _add_connection(self, other_id):
        if self.id == 0:
            return
        assert other_id != self.id
        if other_id != 0:
            assert other_id in self._neighbors
            self._connections.add(other_id)


class Wall:
    """Boundary between two rooms."""
    _a: int
    _b: int
    _tiles: Set[Tuple[int, int]]
    _door: Tuple[int, int]
    def __init__(self, a, b):
        self._a = a
        self._b = b
        self._tiles = set()
        self._doorway = None

    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    def tiles(self):
        return frozenset(self._tiles)

    def adjoins(self, id):
        return self._a == id or self._b == id

    def has_doorway(self):
        return self._doorway != None

    @property
    def doorway(self):
        return self._doorway

    def area(self):
        return len(self._tiles)

    def adjoins(self, room_id):
        return self._a == room_id or self._b == room_id

    # Internal manipulators for use by Builder
    def _add_tile(self, x, y):
        self._tiles.add((x, y))

    def _place_doorway(self, x, y):
        assert self._doorway == None
        assert (x,y) in self._tiles
        self._doorway = (x, y)


class BaseMap:
    rooms: List[Room]
    walls: List[Wall]
    entry: Optional[Tuple[int, int]]
    exit: Optional[Tuple[int, int]]
    def __init__(self, tiles, rooms, walls):
        self.tiles = tiles
        self.rooms = rooms
        self.walls = walls
        self.entry = None
        self.exit = None

    @property
    def shape(self):
        return self.tiles.shape



# Create and manipulate a base map for a game level.
# All mutation happens through calls to the builder.
# Returned objects are either copied or immutable.
class Builder:
    _rooms: Dict[np.uint, Room]
    _walls: Dict[Tuple[int, int], Wall]

    def __init__(self, shape: Tuple[int, int]):
        self.map = np.full(shape, Tile.VOID, dtype=Tile)
        self._rooms = {0: Room(0)}
        self._walls = {}

    # Accessors for array-like properties
    @property
    def shape(self):
        return self.map.shape

    @property
    def width(self):
        return self.map.shape[0]

    @property
    def height(self):
        return self.map.shape[1]


    # Accessors for room graph objects
    def rooms(self):
        for k, v in self._rooms.items():
            if k != 0:
                yield v

    def room_ids(self):
        return frozenset(r.id for r in self.rooms())

    def room(self, id):
        return self._rooms[id]

    def wall_between(self, a_id, b_id):
        return self._walls[self._wall_key(a_id, b_id)]

    def walls_around(self, room_id):
        for w in self._walls.values():
            if w.adjoins(room_id):
                yield w


    # Mutators
    def place_floor(self, x, y, room_id):
        # If there was no floor here, place a tile.
        assert self.map[x, y] == Tile.VOID
        if not room_id:
            return
        self.map[x, y] = Tile.FLOOR
        self._get_room(room_id)._add_tile(x, y)

    def place_horz_wall(self, x, y, above_id, below_id):
        self._place_wall(x, y, above_id, below_id)

    def place_vert_wall(self, x, y, left_id, right_id):
        self._place_wall(x, y, left_id, right_id)

    def place_pillar(self, x, y):
        assert self.map[x, y] == Tile.VOID
        self.map[x, y] = Tile.WALL

    def open_door(self, x, y, a_id, b_id):
        self._open_wall(x, y, a_id, b_id, Tile.DOOR)

    def open_passage(self, x, y, a_id, b_id):
        self._open_wall(x, y, a_id, b_id, Tile.FLOOR)


    # Retrieve finished copy of contents
    def build(self):
        return BaseMap(
            tiles=np.copy(self.map),
            rooms=list(self.rooms()),
            walls=list(self._walls.values())
        )


    # Internal methods
    def _get_room(self, room_id) -> Room:
        """This is the only way to create a Room instance."""
        if room_id not in self._rooms:
            self._rooms[room_id] = Room(room_id)
        return self._rooms[room_id]

    def _wall_key(self, a_id, b_id):
        """Sort IDs consistently, so we only create one wall per pair."""
        return min(a_id, b_id), max(a_id, b_id)

    def _get_wall(self, a_id, b_id) -> Wall:
        """This is the only way to create a Wall instance."""
        # If either wall is the void, return a dummy throwaway wall.
        if a_id == 0 or b_id == 0:
            return Wall(a_id, b_id)
        assert a_id != b_id
        key = self._wall_key(a_id, b_id)
        if key not in self._walls:
            self._walls[key] = Wall(a_id, b_id)
        return self._walls[key]

    def _place_wall(self, x, y, a_id, b_id):
        assert self.map[x, y] == Tile.VOID
        self.map[x, y] = Tile.WALL
        self._get_room(a_id)._add_neighbor(b_id)
        self._get_room(b_id)._add_neighbor(a_id)
        self._get_wall(a_id, b_id)._add_tile(x, y)

    def _open_wall(self, x, y, a_id, b_id, tile_type):
        assert self.map[x, y] == Tile.WALL
        assert a_id in self._rooms
        assert b_id in self._rooms
        assert a_id in self._rooms[b_id]._neighbors
        assert b_id in self._rooms[a_id]._neighbors
        wall = self._get_wall(a_id, b_id)
        assert (x, y) in wall._tiles
        assert not wall.has_doorway()
        wall._place_doorway(x, y)
        self.map[x, y] = tile_type
        self._get_room(a_id)._add_connection(b_id)
        self._get_room(b_id)._add_connection(a_id)

