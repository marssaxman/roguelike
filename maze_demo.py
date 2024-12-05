#!/usr/bin/env python3

import argparse
import numpy as np
import time
import src.maze.render as render
import src.codepoint as U
import src.maze.create as create


def to_chars(grid):
    maze = np.full(shape=grid.shape, dtype=np.uint32, fill_value=U.SPACE)
    palette = render.Palette(
        void=U.SPACE,
        floor=U.FULL_STOP,
        entry=ord(">"),
        exit=ord("<"),
        door=U.PLUS_SIGN,
        door_H=U.BOX_DRAWINGS_LIGHT_QUADRUPLE_DASH_HORIZONTAL,
        door_V=U.BOX_DRAWINGS_LIGHT_TRIPLE_DASH_VERTICAL,
        wall=U.WHITE_SQUARE_CONTAINING_BLACK_SMALL_SQUARE,
        wall_B=U.BOX_DRAWINGS_DOWN_DOUBLE_HORIZONTAL_SINGLE,
        wall_R=U.BOX_DRAWINGS_VERTICAL_SINGLE_RIGHT_DOUBLE,
        wall_RB=U.BOX_DRAWINGS_DOUBLE_DOWN_RIGHT,
        wall_A=U.BOX_DRAWINGS_UP_DOUBLE_HORIZONTAL_SINGLE,
        wall_AB=U.BOX_DRAWINGS_DOUBLE_VERTICAL,
        wall_AR=U.BOX_DRAWINGS_DOUBLE_UP_RIGHT,
        wall_ARB=U.BOX_DRAWINGS_DOUBLE_VERTICAL_RIGHT,
        wall_L=U.BOX_DRAWINGS_VERTICAL_SINGLE_LEFT_DOUBLE,
        wall_LB=U.BOX_DRAWINGS_DOUBLE_DOWN_LEFT,
        wall_LR=U.BOX_DRAWINGS_DOUBLE_HORIZONTAL,
        wall_LRB=U.BOX_DRAWINGS_DOUBLE_DOWN_HORIZONTAL,
        wall_LA=U.BOX_DRAWINGS_DOUBLE_UP_LEFT,
        wall_LAB=U.BOX_DRAWINGS_DOUBLE_VERTICAL_LEFT,
        wall_LAR=U.BOX_DRAWINGS_DOUBLE_UP_HORIZONTAL,
        wall_LARB=U.BOX_DRAWINGS_DOUBLE_VERTICAL_HORIZONTAL,
    )
    render.tiles(grid, maze, palette)
    return maze


def print_maze(maze):
    text = to_chars(maze)
    for y in range(maze.shape[1]):
        line = ""
        for x in range(maze.shape[0]):
            line += chr(text[x, y])
        print(line)


def print_tower(tower):
    for maze in tower:
        print_maze(maze.tiles)
        line = ""
        for x in range(maze.tiles.shape[0]):
            line += "-"
        print(line)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-s",
        "--seed",
        help="specify random generator seed",
        type=int,
    )
    argparser.add_argument(
        "-x",
        "--width",
        help="game board horizontal dimension",
        type=int,
    )
    argparser.add_argument(
        "-y",
        "--height",
        help="game board vertical dimension",
        type=int,
    )
    argparser.add_argument(
        "--box_size",
        help="base grid cell size",
        type=int,
    )
    argparser.add_argument(
        "--stories",
        help="number of levels for three-dimensional maze",
        type=int,
    )
    args = argparser.parse_args()

    seed = args.seed if args.seed else np.int64(time.time_ns())
    rng = np.random.default_rng(seed)

    width = args.width or np.uint(80)
    height = args.height or np.uint(50)
    box_size = args.box_size or max(4, int((width+height)//16))

    print(f"seed: {seed}; x,y=({width},{height}); box_size={box_size}")
    if args.stories:
        tower = create.tower(
            shape=(width, height),
            box_size=box_size,
            stories = args.stories,
            rng=rng
        )
        print_tower(tower)
    else:
        maze = create.level(
            shape=(width, height),
            box_size=box_size,
            rng=rng
        )
        print_maze(maze.tiles)

