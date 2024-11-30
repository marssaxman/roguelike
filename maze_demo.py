#!/usr/bin/env python3

import argparse
import numpy as np
import time
import src.maze.render as render
import src.codepoint as cp
import src.maze.create as create


def to_chars(grid):
    maze = np.full(shape=grid.shape, dtype=np.uint32, fill_value=cp.SPACE)
    palette = render.Palette(
        void=cp.SPACE,
        floor=cp.FULL_STOP,
        door=cp.PLUS_SIGN,
        door_H=cp.BOX_DRAWINGS_LIGHT_QUADRUPLE_DASH_HORIZONTAL,
        door_V=cp.BOX_DRAWINGS_LIGHT_TRIPLE_DASH_VERTICAL,
        wall=cp.COLUMN,
        wall_B=cp.WALL_B,
        wall_R=cp.WALL_R,
        wall_RB=cp.WALL_RB,
        wall_A=cp.WALL_A,
        wall_AB=cp.WALL_AB,
        wall_AR=cp.WALL_AR,
        wall_ARB=cp.WALL_ARB,
        wall_L=cp.WALL_L,
        wall_LB=cp.WALL_LB,
        wall_LR=cp.WALL_LR,
        wall_LRB=cp.WALL_LRB,
        wall_LA=cp.WALL_LA,
        wall_LAB=cp.WALL_LAB,
        wall_LAR=cp.WALL_LAR,
        wall_LARB=cp.WALL_LARB,
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
    args = argparser.parse_args()

    seed = args.seed if args.seed else np.int64(time.time_ns())
    rng = np.random.default_rng(seed)

    width = args.width or np.uint(80)
    height = args.height or np.uint(50)
    box_size = args.box_size or max(4, int((width+height)//16))

    maze = create.level(width=width, height=height, box_size=box_size, rng=rng)
    print(f"seed: {seed}; x,y=({width},{height}); box_size={box_size}")
    print_maze(maze.tiles)

