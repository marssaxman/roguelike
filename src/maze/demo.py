#!/usr/bin/env python3

import numpy as np
import offgrid
import time
import render
import basemap
import connect
import create

def print_maze(maze):
    text = render.to_chars(maze)
    for y in range(maze.shape[1]):
        line = ""
        for x in range(maze.shape[0]):
            line += chr(text[x, y])
        print(line)


if __name__ == '__main__':
    # Everything descends from the random seed; we'll use the current time.
    seed = np.int64(time.time_ns())
    rng = np.random.default_rng(seed)

    try:
        # How big a game board do we want to build, and how big should the
        # average room be?
        width, height = np.uint(80), np.uint(50)
        maze = create.level(width, height, rng)
    except:
        print(f"starting seed: {seed}")
        raise

    # ta-da
    print_maze(maze.tiles)

