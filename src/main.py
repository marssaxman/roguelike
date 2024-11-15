#!/usr/bin/env python3
import tcod

from actions import EscapeAction, MovementAction
from input_handlers import EventHandler

def main():
    # how big should the game window be?
    screen_width = 80
    screen_height = 50
    # where should the player start on screen?
    player_x = screen_width // 2
    player_y = screen_height // 2
    # load the graphics
    tileset = tcod.tileset.load_tilesheet(
        "assets/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )
    # create an object to handle input events
    event_handler = EventHandler()
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
            # clear the console to prepare for drawing
            root_console.clear()
            # print the player
            root_console.print(x=player_x, y=player_y, string="@")
            # show the console inside the game window
            context.present(root_console)
            # wait for an event and respond to it
            for event in tcod.event.wait():
                action = event_handler.dispatch(event)
                if action is None:
                    continue
                elif isinstance(action, MovementAction):
                    player_x += action.dx
                    player_y += action.dy
                elif isinstance(action, EscapeAction):
                    raise SystemExit()


# python magic to call the main function when the program begins
if __name__ == '__main__':
    main()
