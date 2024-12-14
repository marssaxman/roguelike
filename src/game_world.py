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

        box_size = max(4, int((map_shape[0]+map_shape[1])//16))

        self.tower = maze.create.tower(
            shape=map_shape,
            box_size=box_size,
            stories=tower_floors,
            rng=engine.rng,
        )

   def go_to_next_level(self) -> None:
        from procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            map_shape=self.map_shape,
            engine=self.engine,
        )

