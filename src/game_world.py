from typing import Tuple
from engine import Engine


class GameWorld:
   """
   Holds the settings for the GameMap, and generates new maps when moving down
   the stairs.
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

   def generate_floor(self) -> None:
        from procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            map_shape=self.map_shape,
            engine=self.engine,
        )

