from __future__ import annotations

import lzma
import pickle
from typing import Tuple, TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from message_log import MessageLog
import render_functions

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap, GameWorld

class Engine:
    game_map: GameMap
    game_world: GameWorld
    message_log: MessageLog
    mouse_location: Tuple[int, int] # map coordinates, not console coordinates
    player: Actor
    rng: np.random.Generator

    def __init__(self, player: Actor, rng: np.random.Generator):
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player
        self.rng = rng

    def save_as(self, filename: str) -> None:
        """Save this game engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass # ignore impossible actions by the AI

    def update_fov(self) -> None:
        """Recompute the visible area based on the player's point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        # If a tile is visible, add it to the "explored" map.
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        self.game_map.render(console.rgb[:, :-7])
        log_y = console.height - 5
        log_w = console.width - 21
        self.message_log.render(console=console, x=21, y=log_y, width=log_w, height=5)
        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            location=(0, log_y),
            total_width=20,
        )
        level_y = console.height - 3
        render_functions.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(0, level_y),
        )
        names_y = console.height - 6
        render_functions.render_names_at_mouse_location(
            console=console,
            x=21,
            y=names_y,
            engine=self
        )

