#!/usr/bin/env python3
import copy
import tcod
import color

from engine import Engine
import entity_factories
from entity import Entity
from procgen import generate_dungeon

from random import randrange

def main():
    # how big should the game window be?
    screen_width = 80
    screen_height = 50
    # how big should the map be?
    map_width = 80
    map_height = 43
    # what kind of dungeon should we build?
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    # how should it be populated with enemies?
    max_monsters_per_room = 2

    # load the graphics
    tileset = tcod.tileset.load_tilesheet(
        "assets/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )
    player = copy.deepcopy(entity_factories.player)
    engine = Engine(player=player)
    engine.game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        engine=engine,
    )
    engine.update_fov()
    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text
    )

    # create a terminal window to put the game interface in
    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset = tileset,
        title = "Roguelike Game Experiment",
        vsync = True,
    ) as context:
        # create a console inside the window we can draw into
        root_console = tcod.console.Console(
            screen_width, screen_height, order="F"
        )
        # run the game loop forever
        while True:
            root_console.clear()
            engine.event_handler.on_render(console=root_console)
            context.present(root_console)
            engine.event_handler.handle_events(context)

# python magic to call the main function when the program begins
if __name__ == '__main__':
    main()
