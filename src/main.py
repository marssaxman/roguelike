#!/usr/bin/env python3
import traceback
import tcod
import color
import exceptions
import setup_game
import input_handlers
from entity import Entity
from random import randrange
import graphics


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

    # Override the box-drawing characters TCOD uses for frames with some
    # curvy, dimensional tiles from the Oddball set.
    oddball_tiles = tcod.tileset.load_tilesheet(
        "assets/Oddball_16x16.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )
    # top left corner
    tileset.set_tile(0x250C, oddball_tiles.get_tile(0x2554))
    # horizontal bar
    tileset.set_tile(0x2500, oddball_tiles.get_tile(0x2550))
    # top right corner
    tileset.set_tile(0x2510, oddball_tiles.get_tile(0x2557))
    # vertical bar
    tileset.set_tile(0x2502, oddball_tiles.get_tile(0x2551))
    # bottom left corner
    tileset.set_tile(0x2514, oddball_tiles.get_tile(0x255A))
    # bottom right corner
    tileset.set_tile(0x2518, oddball_tiles.get_tile(0x255D))

    # Load all the game graphics, assigning them private-use characters.
    graphics.load_into(tileset)

    return tileset

def main():
    # how big should the game window be?
    screen_width = 60
    screen_height = 30

    tileset = load_tiles()
    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

    # create a terminal window to put the game interface in
    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset = tileset,
        title = "bob's house of uncleanliness",
        vsync = True,
        sdl_window_flags=tcod.context.SDL_WINDOW_MAXIMIZED,
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
                context.present(root_console, integer_scaling=True)

                try:
                    for event in tcod.event.wait(timeout=0.3):
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
                    else:
                        raise
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
