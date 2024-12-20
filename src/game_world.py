from typing import Tuple
from engine import Engine
import maze.create

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
        self.tower = maze.create.tower(
            shape=map_shape,
            box_size=box_size,
            stories=tower_floors,
            rng=engine.rng,
        )

   def go_to_next_level(self) -> None:
        from procgen import generate_dungeon
        # The dungeon generator thinks the game begins at level 1, but the
        # tower generator returns an array, which begins at level 0, and
        # that's why we add 1 to the `floor` parameter instead of incrementing
        # `current_floor` before calling `generate_dungeon`.
        self.engine.game_map = generate_dungeon(
            base_map = self.tower[self.current_floor],
            engine=self.engine,
            floor=self.current_floor+1
        )
        self.current_floor += 1

