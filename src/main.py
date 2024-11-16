#!/usr/bin/env python3
import copy
import tcod

from engine import Engine
import entity_factories
from entity import Entity
from input_handlers import EventHandler
from procgen import generate_dungeon

from random import randrange

def main():
    # how big should the game window be?
    screen_width = 80
    screen_height = 50
    # how big should the map be?
    map_width = 80
    map_height = 45
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
    # create an object to handle input events
    event_handler = EventHandler()

    # create some objects: a player and an npc
    player = copy.deepcopy(entity_factories.player)
    game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        player=player
    )

    engine = Engine(
        event_handler=event_handler, game_map=game_map, player=player
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
            # Draw the game board, with all of its entities
            engine.render(console=root_console, context=context)
            # Wait for the next event
            events = tcod.event.wait()
            # Tell the game engine to handle the events
            engine.handle_events(events)

# python magic to call the main function when the program begins
if __name__ == '__main__':
    main()
