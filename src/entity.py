from __future__ import annotations

import copy
import math
from typing import Optional, Tuple, TypeVar, TYPE_CHECKING, Union, Type

from render_order import RenderOrder
from components import appearance

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.consumable import Consumable
    from components.equipment import Equipment
    from components.equippable import Equippable
    from components.fighter import Fighter
    from components.inventory import Inventory
    from components.level import Level
    from components.appearance import Appearance
    from components.mechanism import Mechanism
    from game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    parent: Union[GameMap, Inventory]
    def __init__(
        self,
        parent: Optional[GameMap] = None,
        x: int = 0,
        y: int = 0,
        appearance: Appearance = appearance.Default(),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.LAST,
        mobile: bool = False,
    ):
        self.x = x
        self.y = y
        self.appearance = appearance
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        self.mobile = mobile
        if parent:
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this entity at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """Place this entity at a new location. Handles moving across maps."""
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"): # possibly uninitialized?
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """Return the distance between this entity and the given point."""
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy
        # Inform the appearance, in case it changes with direction
        self.appearance.move(dx, dy)


class Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        appearance: Appearance = appearance.Default(),
        name: str = "<Unnamed>",
        ai_cls: Type[BaseAI],
        equipment: Equipment,
        fighter: Fighter,
        inventory: Inventory,
        level: Level,
    ):
        super().__init__(
            x=x,
            y=y,
            appearance=appearance,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
            mobile=True,
        )
        self.ai: Optional[BaseAI] = ai_cls(self)

        self.equipment: Equipment = equipment
        self.equipment.parent = self

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

        self.level = level
        self.level.parent = self

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)


class Item(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        appearance: Appearance = appearance.Default(),
        name: str = "<Unnamed>",
        consumable: Optional[Consumable] = None,
        equippable: Optional[Equippable] = None,
    ):
        super().__init__(
            x=x,
            y=y,
            appearance=appearance,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
            mobile=False,
        )

        self.consumable = consumable

        if self.consumable:
            self.consumable.parent = self

        self.equippable = equippable

        if self.equippable:
            self.equippable.parent = self


class Fixture(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        appearance: Appearance = appearance.Default(),
        name: str = "<Unnamed>",
        mechanism: Optional[Mechanism] = None,
    ):
        super().__init__(
            x=x,
            y=y,
            appearance=appearance,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.FIXTURE,
            mobile=False,
        )
        self.mechanism = mechanism
        if self.mechanism:
            self.mechanism.parent = self

