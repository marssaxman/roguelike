from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from components.base_component import BaseComponent
from entity import Actor, Fixture
import color

class Mechanism(BaseComponent):
    """A mechanism can be operated by an actor to perform an effect."""
    parent: Fixture

    def __init__(self):
        pass

    def operate(self, entity: Actor) -> None:
        raise NotImplementedError()



class DownStairs(Mechanism):
    """Descend the stairs to a lower level."""
    def operate(self, entity: Actor) -> None:
        """Move this entity to a lower-level game map."""
        if entity is self.engine.player:
            self.engine.game_world.go_to_prev_level()
            self.engine.message_log.add_message(
                "You descend the staircase.", color.descend
            )
        else:
            self.engine.message_log.add_message(
                f"{entity.name} wants to descend the stairs", color.impossible
            )


class UpStairs(Mechanism):
    """Ascend the stairs to a higher level."""
    def operate(self, entity: Actor) -> None:
        if entity is self.engine.player:
            self.engine.game_world.go_to_next_level()
            self.engine.message_log.add_message(
                "You ascend the staircase.", color.ascend
            )
        else:
            self.engine.message_log.add_message(
                f"{entity.name} wants to ascend the stairs", color.impossible
            )


class DoorOutside(Mechanism):
    """Exit the tower and end the game."""
    def operate(self, entity: Actor) -> None:
        # Only the player can leave the tower.
        if entity is not self.engine.player:
            return
        self.engine.message_log.add_message(
            f"The door outside is firmly locked.", color.impossible
        )

