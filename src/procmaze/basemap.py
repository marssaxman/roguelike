# Build a map, composed of tiles.

import numpy as np
from enum import Enum
from typing import Dict, Set, Tuple

class Tile(Enum):
    VOID = 0,
    WALL = 1,
    FLOOR = 2,
    DOOR = 3


class Room:
    id: int
    _tiles: Set[Tuple[int, int]]
    _neighbors: Set[int]
    def __init__(self, id: int):
        self.id = id
        self._tiles = set()
        self._neighbors = set()

    # Public accessors
    def is_empty(self):
        return 0 == len(self._tiles)

    def tiles(self):
        for x, y in self._tiles:
            yield x, y

    def neighbors(self):
        """Iterate over neighbor IDs"""
        for k in self._neighbors:
            yield k

    # Internal manipulators for use by Builder
    def _add_tile(self, x, y):
        self._tiles.add((x, y))

    def _add_neighbor(self, other_id):
        assert other_id != self.id
        if other_id != 0:
            self._neighbors.add(other_id)

    def _remove_neighbor(self, other_id):
        if other_id in self._neighbors:
            self._neighbors.remove(other_id)


class Void:
    """Convenience dummy which acts like Room"""
    def __init__(self):
        pass

    @property
    def id(self):
        return 0

    def is_empty(self):
        return True

    def tiles(self):
        return
        yield

    def neighbors(self):
        return
        yield

    def _add_neighbor(self, id):
        pass



# Create and manipulate a base map for a game level.
# All mutation happens through calls to the builder.
# Returned objects are either copied or immutable.
class Builder:
    _rooms: Dict[np.uint, Room]

    def __init__(self, width: np.uint, height: np.uint):
        self.map = np.full((width, height), Tile.VOID, dtype=Tile)
        self._rooms = {0: Void()}

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


    # Mutators
    def place_floor(self, x, y, room_id):
        # If there was no floor here, place a tile.
        assert self.map[x, y] == Tile.VOID
        if not room_id:
            return
        self.map[x, y] = Tile.FLOOR
        self._get_room(room_id)._add_tile(x, y)

    def place_horz_wall(self, x, y, above_id, below_id):
        assert self.map[x, y] == Tile.VOID
        self.map[x, y] = Tile.WALL
        self._get_room(above_id)._add_neighbor(below_id)
        self._get_room(below_id)._add_neighbor(above_id)

    def place_vert_wall(self, x, y, left_id, right_id):
        assert self.map[x, y] == Tile.VOID
        self.map[x, y] = Tile.WALL
        self._get_room(left_id)._add_neighbor(right_id)
        self._get_room(right_id)._add_neighbor(left_id)

    def place_pillar(self, x, y):
        assert self.map[x, y] == Tile.VOID
        self.map[x, y] = Tile.WALL

    def delete_room(self, id: int):
        assert id in self._rooms
        room = self._rooms[id]
        for n_id in room.neighbors():
            self._rooms[n_id]._remove_neighbor(id)
        for x,y in room.tiles():
            assert self.map[x, y] == Tile.FLOOR
            self.map[x, y] == Tile.VOID
        del self._rooms[id]


    # Retrieve finished copy of contents
    def get_tiles(self):
        return np.copy(self.map)


    # Internal methods
    def _get_room(self, room_id) -> Room:
        """This is the only way to create a Room instance."""
        if room_id not in self._rooms:
            self._rooms[room_id] = Room(room_id)
        return self._rooms[room_id]

