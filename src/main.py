#!/usr/bin/env python3
import traceback
import tcod
import color
import exceptions
import setup_game
import input_handlers
from entity import Entity
from random import randrange


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active engine, then save it."""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")

def main():
    # how big should the game window be?
    screen_width = 80
    screen_height = 50

    # load the graphics
    tileset = tcod.tileset.load_tilesheet(
        "assets/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

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
