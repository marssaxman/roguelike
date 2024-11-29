#!/usr/bin/env python3
import traceback
import tcod
import color
import exceptions
import setup_game
import input_handlers
from entity import Entity
from random import randrange
import codepoint


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active engine, then save it."""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")

def load_tiles():
    # load the main font
    tileset = tcod.tileset.load_tilesheet(
        "assets/Cooz_curses_square_16x16.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )

    # load some graphics
    wall_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Objects/Wall.png", (320//16), (816//16), range(1020)
    )
    # 20 tiles in a row, 51 rows
    # Wall tiles exist in a 6x3 cluster with 1 space between columns
    # Clusters exist in a 4-high group (6x12 tiles) of color variants
    # We'll use the brick cluster in row 1
    # Within a cluster, tiles are located like thus:
    # RB    LR    LB    #       LRB
    # AB    A           ARB     LARB    LAB
    # AR          LA            LAR
    # (B = AB, L = AL, R=AR)
    tileset.set_tile(codepoint.WALL, wall_tiles.get_tile(63))
    tileset.set_tile(codepoint.WALL_L, wall_tiles.get_tile(61))
    tileset.set_tile(codepoint.WALL_A, wall_tiles.get_tile(81))
    tileset.set_tile(codepoint.WALL_R, wall_tiles.get_tile(61))
    tileset.set_tile(codepoint.WALL_B, wall_tiles.get_tile(80))
    tileset.set_tile(codepoint.WALL_LR, wall_tiles.get_tile(61))
    tileset.set_tile(codepoint.WALL_AB, wall_tiles.get_tile(80))
    tileset.set_tile(codepoint.WALL_RB, wall_tiles.get_tile(60))
    tileset.set_tile(codepoint.WALL_LB, wall_tiles.get_tile(62))
    tileset.set_tile(codepoint.WALL_AR, wall_tiles.get_tile(100))
    tileset.set_tile(codepoint.WALL_LA, wall_tiles.get_tile(102))
    tileset.set_tile(codepoint.WALL_ARB, wall_tiles.get_tile(83))
    tileset.set_tile(codepoint.WALL_LAB, wall_tiles.get_tile(85))
    tileset.set_tile(codepoint.WALL_LRB, wall_tiles.get_tile(64))
    tileset.set_tile(codepoint.WALL_LAR, wall_tiles.get_tile(104))
    tileset.set_tile(codepoint.WALL_LARB, wall_tiles.get_tile(84))

    door_tiles = tcod.tileset.load_tilesheet(
        "assets/DawnLike/Objects/Door0.png", 8, 6, range(48)
    )
    tileset.set_tile(codepoint.DOOR, door_tiles.get_tile(0))

    return tileset

def main():
    # how big should the game window be?
    screen_width = 80
    screen_height = 50

    tileset = load_tiles()
    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

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
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit.
            save_game(handler, "savegame.sav")
            raise
        except BaseException:  # Save on any other unexpected exception.
            save_game(handler, "savegame.sav")
            raise

      
# python magic to call the main function when the program begins
if __name__ == '__main__':
    main()
