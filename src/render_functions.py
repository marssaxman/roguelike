from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import color

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine
    from game_map import GameMap


def render_bar(
    console: Console,
    current_value: int,
    maximum_value: int,
    location: Tuple[int, int],
    total_width: int
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)
    x, y = location

    console.draw_rect(x=x, y=y, width=total_width, height=1, ch=1, bg=color.bar_empty)
    if bar_width > 0:
        console.draw_rect(
            x=x, y=y, width=bar_width, height=1, ch=1, bg=color.bar_filled
        )

    console.print(
        x=x+1, y=y, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text
    )

def render_dungeon_level(
    console: Console, dungeon_level: int, location: Tuple[int, int]
) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    x, y = location

    console.print(x=x, y=y, string=f"Dungeon level: {dungeon_level}")


def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    """
    Print names of entities on the last map tile the mouse pointed at.
    """
    mouse_x, mouse_y = engine.mouse_location
    names_at_cursor = engine.game_map.get_names_at_location(mouse_x, mouse_y)
    console.print(x=x, y=y, string=names_at_cursor)
