from __future__ import annotations

from typing import Iterable, Iterator, Optional, Tuple, TYPE_CHECKING
from numpy.typing import NDArray

import numpy as np  # type: ignore
from tcod.console import Console

from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(
        self,
        engine: Engine,
        shape: Tuple[int, int],
        entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = shape
        self.entities = set(entities)
        self.tiles = np.full(shape, fill_value=tile_types.wall, order="F")
        self.visible = np.full(shape, fill_value=False, order="F")
        self.explored = np.full(shape, fill_value=False, order="F")
        self.downstairs_location = (0, 0)

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this map's living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(
        self, location_x: int, location_y: int
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity
        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor
        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height


    def get_viewport(self, window_shape: Tuple[int, int]):
        """
        Given the shape of a display window, find the viewable region.

        If the window is larger than the map, we will try to center the
        viewport on the player, until the player is too close to an edge to
        make this work without displaying tiles that would be outside the map.
        """
        x = self.engine.player.x
        y = self.engine.player.y
        view_width = min(window_shape[0], self.width)
        view_height = min(window_shape[1], self.height)
        half_width = int(view_width / 2)
        half_height = int(view_height / 2)
        # Try to center the viewport on the player, but don't scroll off the
        # left or top edges of the map.
        left = max(x - half_width, 0)
        top = max(y - half_height, 0)
        right = left + view_width
        bottom = top + view_height
        # Do not scroll off the bottom or right edges of the map, either.
        if right > self.width:
            left -= (right - self.width)
            right = self.width
            if left < 0:
                left = 0
        if bottom > self.height:
            top -= (bottom - self.height)
            bottom = self.height
            if top < 0:
                top = 0
        # Return the map-coordinates for the viewport.
        return (left, top, right, bottom)


    def render(self, window: NDArray[Any]) -> None:
        """
        Renders the map into the given tile buffer.

        If the map is larger than the buffer, attempt to center the viewpoint
        on the player. If the map is smaller than the buffer, letterbox it
        with the SHROUD texture.

        Tiles which are currently visible will be rendered with their "light"
        style; tiles which have previously been visible will be rendered with
        "dark" style; everything else will be drawn under "SHROUD".
        """
        # Get the bounding box of the viewport, in map coordinates, sized to
        # match the display window.
        view_rect = self.get_viewport(window.shape)
        view_left, view_top, view_right, view_bottom = view_rect
        views_horz = slice(view_left, view_right)
        views_vert = slice(view_top, view_bottom)

        # Get views on the map, sized & positioned to match the viewport.
        # Select the display style for each tile based on its visibility.
        view_tiles = self.tiles[views_horz, views_vert]
        view_visible = self.visible[views_horz, views_vert]
        view_explored = self.explored[views_horz, views_vert]
        style_tiles = np.select(
            condlist=[view_visible, view_explored],
            choicelist=[view_tiles["light"], view_tiles["dark"]],
            default=tile_types.SHROUD,
        )

        # Render the styled tiles to the window. If the tiled area is smaller
        # than the window, letterbox it filling with SHROUD.
        win_width, win_height = window.shape
        view_width, view_height = style_tiles.shape
        adjust_x, adjust_y = view_left, view_top
        win_horz = slice(0, win_width)
        win_vert = slice(0, win_height)
        if win_width > view_width:
            gap = (win_width - view_width) // 2
            adjust_x -= gap
            # draw left side letterbox
            window[0:gap, :] = tile_types.SHROUD
            # position viewport in the center of the window
            win_horz = slice(gap, view_width + gap)
            # draw right side letterbox
            window[view_width + gap:, :] = tile_types.SHROUD
        if win_height > view_height:
            gap = (win_height - view_height) // 2
            adjust_y -= gap
            # draw letterbox above
            window[:, :gap] = tile_types.SHROUD
            # position viewport in the center of the window
            win_vert = slice(gap, view_height + gap)
            # draw letterbox below
            window[:, view_height + gap:] = tile_types.SHROUD
        # Draw the map contents.
        window[win_horz, win_vert] = style_tiles

        # Draw visible entities in priority order on top of the rendered tiles.
        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )
        for entity in entities_sorted_for_rendering:
            if not self.visible[entity.x, entity.y]:
                continue
            char = entity.char
            # entity char can be a string or a codepoint; we draw codepoints
            if isinstance(char, str):
                char = ord(char)
            x, y = entity.x - adjust_x, entity.y - adjust_y
            # reuse the tile's existing background color
            bg = window[x, y][2]
            window[x, y] = (char, entity.color, bg)


class GameWorld:
   """
   Holds the settings for the GameMap, and generates new maps when moving down the stairs.
   """

   def __init__(
        self,
        *,
        engine: Engine,
        map_shape: Tuple[int, int],
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        current_floor: int = 0
    ):
        self.engine = engine
        self.map_shape = map_shape
        self.max_rooms = max_rooms
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size
        self.current_floor = current_floor

   def generate_floor(self) -> None:
        from procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_shape=self.map_shape,
            engine=self.engine,
        )

