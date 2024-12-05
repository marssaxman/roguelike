from __future__ import annotations

from typing import Dict, Iterator, List, Tuple, TYPE_CHECKING

import tcod
import numpy as np

import entity_factories
from game_map import GameMap
import tile_types
import maze.create
import maze.render
from maze import basemap


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
    0: [(entity_factories.health_potion, 35)],
    2: [(entity_factories.confusion_scroll, 10)],
    4: [(entity_factories.lightning_scroll, 25), (entity_factories.sword, 5)],
    6: [(entity_factories.fireball_scroll, 25), (entity_factories.chain_mail, 15)],
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.orc, 80), (entity_factories.rat, 100)],
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
    rng: np.random.Generator,
):
    """Populate all of these rooms with appropriate entities for the level."""
    floor = dungeon.engine.game_world.current_floor
    for room in rooms:
        # Put some monsters in the room
        place_entities(room, dungeon, floor, rng)
    # Put the exit stairway somewhere in the last room
    stairs_x, stairs_y = room.random_location(rng)
    dungeon.tiles[stairs_x, stairs_y] = tile_types.down_stairs
    dungeon.downstairs_location = stairs_x, stairs_y


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_shape: Tuple[int, int],
    engine: Engine,
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_shape, entities=[player])

    # temporary: this should become part of the Engine
    rng = np.random.default_rng()
    level = maze.create.level(shape=map_shape, rng=rng)

    palette = maze.render.Palette(
        void = tile_types.wall,
        floor = tile_types.floor,
        entry = tile_types.floor,
        exit = tile_types.floor,
        door = tile_types.door,
        door_H = tile_types.door_H,
        door_V = tile_types.door_V,
        wall = tile_types.wall,
        wall_B = tile_types.wall_B,
        wall_R = tile_types.wall_R,
        wall_RB = tile_types.wall_RB,
        wall_A = tile_types.wall_A,
        wall_AB = tile_types.wall_AB,
        wall_AR = tile_types.wall_AR,
        wall_ARB = tile_types.wall_ARB,
        wall_L = tile_types.wall_L,
        wall_LB = tile_types.wall_LB,
        wall_LR = tile_types.wall_LR,
        wall_LRB = tile_types.wall_LRB,
        wall_LA = tile_types.wall_LA,
        wall_LAB = tile_types.wall_LAB,
        wall_LAR = tile_types.wall_LAR,
        wall_LARB = tile_types.wall_LARB,
    )
    maze.render.tiles(level.tiles, dungeon.tiles, palette)

    # Get only the non-corridor rooms.
    rooms = [r for r in level.rooms if not r.is_corridor()]
    # Position the player in an arbitrarily chosen room.
    start_point = rooms[0].random_location(rng)
    player.place(*start_point, dungeon)
    # Populate each room with appropriate entities.
    populate_rooms(dungeon, rooms, rng)

    return dungeon
