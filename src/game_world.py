from typing import Tuple
from engine import Engine
import maze.create
from procgen import generate_dungeon

class GameWorld:
   """
   Contains all the state for the entire game.
   """

   def __init__(
        self,
        *,
        engine: Engine,
        map_shape: Tuple[int, int],
        tower_floors: int,
        current_floor: int = 0
    ):
        self.engine = engine
        self.map_shape = map_shape
        self.tower_floors = tower_floors
        self.current_floor = current_floor
        box_size = 8
        base_tower = maze.create.tower(
            shape=map_shape,
            box_size=box_size,
            stories=tower_floors,
            rng=engine.rng,
        )
        self.tower = [generate_dungeon(
            base_map = base_map,
            engine=self.engine,
            floor=floor+1
        ) for floor, base_map in enumerate(base_tower)]

   def go_to_starting_level(self) -> None:
        game_map = self.tower[0]
        self.engine.game_map = game_map
        assert game_map.entry_location
        x, y = game_map.entry_location
        tiles = game_map.tiles
        assert not tiles[x,y]["walkable"]
        if (y+1) < tiles.shape[1] and tiles[x,y+1]["walkable"]:
            self.engine.player.place(x, y+1, game_map)
        else:
            assert y > 0 and tiles[x,y-1]["walkable"]
            self.engine.player.place(x, y-1, game_map)
        self.current_floor = 1

   def go_to_next_level(self) -> None:
        # The dungeon generator thinks the game begins at level 1, but the
        # tower generator returns an array, which begins at level 0, and
        # that's why we add 1 to the `floor` parameter instead of incrementing
        # `current_floor` before calling `generate_dungeon`.
        game_map = self.tower[self.current_floor]
        self.engine.game_map = game_map
        assert game_map.entry_location
        x, y = game_map.entry_location
        self.engine.player.place(x, y, game_map)
        self.current_floor += 1

   def go_to_prev_level(self) -> None:
        self.current_floor -= 1
        game_map = self.tower[self.current_floor-1]
        self.engine.game_map = game_map
        assert game_map.exit_location
        x, y = game_map.exit_location
        self.engine.player.place(x, y, game_map)

