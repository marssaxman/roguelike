from __future__ import annotations

from typing import Dict, Iterator, List, Tuple, TYPE_CHECKING
from dataclasses import dataclass

import tcod
import numpy as np

import entity_factories
from game_map import GameMap
import tile_types
import maze.create
import maze.render
from maze import basemap
import graphics


if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

max_items_by_floor = [
    (1, 1),
    (4, 2),
 ]

max_monsters_by_floor = [
    (1, 2),
    (4, 3),
    (6, 5),
 ]

item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.health_potion, 35), (entity_factories.confusion_scroll, 5)],
    2: [(entity_factories.confusion_scroll, 10)],
    4: [(entity_factories.lightning_scroll, 25), (entity_factories.sword, 5)],
    6: [(entity_factories.fireball_scroll, 25), (entity_factories.chain_mail, 15)],
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [
        (entity_factories.orc, 80),
        (entity_factories.rat, 100),
        (entity_factories.silly, 20)
    ],
    3: [(entity_factories.troll, 15)],
    5: [(entity_factories.troll, 30)],
    7: [(entity_factories.troll, 60)],
    8: [(entity_factories.rat, 0)],
}


def get_max_value_for_floor(
    weighted_chances_by_floor: List[Tuple[int, int]], floor: int
 ) -> int:
    current_value = 0

    for floor_minimum, value in weighted_chances_by_floor:
        if floor_minimum > floor:
            break
        else:
            current_value = value

    return current_value


def get_entities_at_random(
    weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int]]],
    number_of_entities: int,
    floor: int,
    rng: np.random.Generator
 ) -> List[Entity]:
    entity_weighted_chances = {}

    for key, values in weighted_chances_by_floor.items():
        if key > floor:
            break
        else:
            for value in values:
                entity = value[0]
                weighted_chance = value[1]

                entity_weighted_chances[entity] = weighted_chance

    entities = list(entity_weighted_chances.keys())
    entity_chance_weights = list(entity_weighted_chances.values())

    # get p-values by dividing each value by the sum of the weights
    total_weight = np.sum(entity_chance_weights)
    entity_probabilities = np.divide(entity_chance_weights, total_weight)
    chosen_entities = rng.choice(
        entities, size=number_of_entities, p=entity_probabilities
    )
    return chosen_entities.tolist()


def place_entities(
    room: Room,
    dungeon: GameMap,
    floor_number: int,
    rng: np.random.Generator
) -> None:
    number_of_monsters = rng.integers(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number),
        endpoint=True
    )
    number_of_items = rng.integers(
        0, get_max_value_for_floor(max_items_by_floor, floor_number),
        endpoint=True
    )
    monsters: List[Entity] = get_entities_at_random(
        enemy_chances, number_of_monsters, floor_number, rng
    )
    items: List[Entity] = get_entities_at_random(
        item_chances, number_of_items, floor_number, rng
    )
    for entity in monsters + items:
        x, y = room.random_location(rng)
        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity.spawn(dungeon, x, y)


def populate_rooms(
    dungeon: GameMap,
    rooms: Iterator[RectangularRoom],
    floor: int,
    rng: np.random.Generator,
):
    """Populate all of these rooms with appropriate entities for the level."""
    for room in rooms:
        # Put some monsters in the room
        place_entities(room, dungeon, floor, rng)
    # Put the exit stairway somewhere in the last room
    stairs_x, stairs_y = room.random_location(rng)
    dungeon.tiles[stairs_x, stairs_y] = tile_types.exit_stairs
    dungeon.exit_location = stairs_x, stairs_y

@dataclass
class RoomStyle:
    floor_glyphs: graphics.FloorTiles
    wall_glyphs: graphics.WallTiles


def style_rooms(
    base_map: maze.basemap.BaseMap,
    rng: np.random.Generator,
):
    room_styles: Dict[int, RoomStyle] = dict()
    for room in base_map.rooms:
        # Pick a floor style completely at random.
        floor_style = rng.integers(0, len(graphics.FLOORS))
        floor_glyphs = graphics.FLOORS[floor_style]
        wall_style = rng.integers(0, len(graphics.WALLS))
        wall_glyphs = graphics.WALLS[wall_style]
        room_styles[room.id] = RoomStyle(
            floor_glyphs=floor_glyphs,
            wall_glyphs=wall_glyphs
        )
    return room_styles

def paint_floors(
    base_map: maze.basemap.BaseMap,
    dungeon: GameMap,
    room_styles: Dict[int, RoomStyle],
    rng: np.random.Generator,
):
    """Paint the dungeon with floor tiles appropriate to each room."""
    map_shape = base_map.shape
    out = np.zeros_like(base_map.tiles, dtype=np.uint)
    for room in base_map.rooms:
        glyphs = room_styles[room.id].floor_glyphs
        tiles = base_map.tiles
        WALL = basemap.Tile.WALL
        for x, y in room.tiles():
            left = x > 0 and tiles[x-1, y] != WALL
            above = y > 0 and tiles[x, y-1] != WALL
            right = (x+1) < map_shape[0] and tiles[x+1, y] != WALL
            below = (y+1) < map_shape[1] and tiles[x, y+1] != WALL
            code = glyphs.pick(left=left, above=above, right=right, below=below)
            dungeon.tiles[x,y] = tile_types.new_floor(code)
            out[x, y] = room.id
    return out

def paint_doors(
    base_map: maze.basemap.BaseMap,
    room_grid,
    dungeon: GameMap,
    room_styles: Dict[int, RoomStyle],
    rng: np.random.Generator,
):
    WALL = basemap.Tile.WALL
    DOOR = basemap.Tile.DOOR
    for wall in base_map.walls:
        if not wall.has_door():
            continue
        # Is it a vertical or horizontal door?
        # Every door must have either walls above and below, or left and right.
        x, y = wall.door
        if base_map.tiles[x, y-1] == WALL:
            assert base_map.tiles[x, y+1] == WALL
            assert base_map.tiles[x-1, y] != WALL
            assert base_map.tiles[x+1, y] != WALL
            # Vertical door: use adjoining tile left & right
            left_room_id = room_grid[x-1, y]
            left_glyphs = room_styles[left_room_id].floor_glyphs
            right_room_id = room_grid[x+1, y]
            right_glyphs = room_styles[right_room_id].floor_glyphs
            left_code = left_glyphs.pick(left=True, right=True)
            right_code = right_glyphs.pick(left=True, right=True)
            pass_code = graphics.adjoin(left_code, right_code)
            if base_map.tiles[x,y] == DOOR:
                # doorway
                door_code = graphics.composite(pass_code, graphics.DOOR_V)
                dungeon.tiles[x,y] = tile_types.new_door(door_code)
            else:
                # open passageway
                dungeon.tiles[x,y] = tile_types.new_floor(pass_code)
        elif base_map.tiles[x-1, y] == WALL:
            assert base_map.tiles[x+1, y] == WALL
            assert base_map.tiles[x, y-1] != WALL
            assert base_map.tiles[x, y+1] != WALL
            # Horizontal door: use lower tile
            below_room_id = room_grid[x, y+1]
            glyphs = room_styles[below_room_id].floor_glyphs
            pass_code = glyphs.pick(above=True, below=True)
            if base_map.tiles[x,y] == DOOR:
                # doorway
                door_code = graphics.composite(pass_code, graphics.DOOR_H)
                dungeon.tiles[x,y] = tile_types.new_door(door_code)
            else:
                # open passageway
                dungeon.tiles[x,y] = tile_types.new_floor(pass_code)

def paint_walls(
    base_map: maze.basemap.BaseMap,
    room_grid,
    dungeon: GameMap,
    room_styles: Dict[int, RoomStyle],
    rng: np.random.Generator,
):
    map_shape = room_grid.shape
    assert map_shape == base_map.tiles.shape
    assert map_shape == dungeon.tiles.shape
    WALL = basemap.Tile.WALL
    tiles = base_map.tiles
    for x, y in np.ndindex(map_shape):
        if base_map.tiles[x, y] != WALL:
            continue
        left = x > 0 and tiles[x-1, y] == WALL
        above = y > 0 and tiles[x, y-1] == WALL
        right = (x+1) < map_shape[0] and tiles[x+1, y] == WALL
        below = (y+1) < map_shape[1] and tiles[x, y+1] == WALL
        # Wall style is tricky because walls take their style from rooms,
        # which are defined by floors. Horizontal walls use the style defined
        # by the room below; vertical walls use both the left and the right
        # styles, split down the middle.

        # temporary hack
        glyphs = graphics.WALLS[0]
        code = glyphs.pick(left=left, above=above, right=right, below=below)
        dungeon.tiles[x,y] = tile_types.new_wall(code)


def generate_dungeon(
    base_map: maze.basemap.BaseMap,
    engine: Engine,
    floor: int,
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player

    rng = engine.rng
    map_shape = base_map.shape
    dungeon = GameMap(engine, map_shape, entities=[player])

    room_styles = style_rooms(base_map, rng=rng)
    room_grid = paint_floors(
        base_map=base_map,
        dungeon=dungeon,
        room_styles=room_styles,
        rng=rng
    )
    paint_doors(
        base_map=base_map,
        room_grid=room_grid,
        dungeon=dungeon,
        room_styles=room_styles,
        rng=rng
    )
    paint_walls(
        base_map=base_map,
        room_grid=room_grid,
        dungeon=dungeon,
        room_styles=room_styles,
        rng=rng
    )

    # Get only the non-corridor rooms.
    rooms = [r for r in base_map.rooms if not r.is_corridor()]
    # Position the player in an arbitrarily chosen room.
    start_point = rooms[0].random_location(rng)
    player.place(*start_point, dungeon)
    # Populate each room with appropriate entities.
    populate_rooms(dungeon, rooms, floor=floor, rng=rng)

    return dungeon
