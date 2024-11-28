#!/usr/bin/env python3

import numpy as np
import offgrid
import time
import render
import basemap

def rasterize(width: np.uint, height: np.uint, rects):
    # Allocate an extra row and column, which will be left empty;
    # this means we can skip the range checks when scanning 2x2 boxes.
    shape = (np.add(width, 1, dtype=np.uint), np.add(height, 1, dtype=np.uint))
    grid = np.zeros(shape, dtype=np.uint)
    counter = 0
    for rect in rects:
        left, top, right, bottom = rect
        # Skip rects that don't lie completely within the requested area
        if left <= 0 or top <= 0 or right > width or bottom > height:
            continue;
        # Increment the room counter and assign it to the cell region
        counter += 1
        grid[left:right, top:bottom] = counter
    return grid


def apply_grid(grid, builder):
    for x, y in np.ndindex(builder.shape):
        # Get the four room indexes touching this grid junction
        tl = grid[x, y]
        tr = grid[x+1, y]
        bl = grid[x, y+1]
        br = grid[x+1, y+1]
        if tl == tr == bl == br:
            builder.place_floor(x, y, tl)
        elif tl == tr and bl == br:
            builder.place_horz_wall(x, y, tl, bl)
        elif tl == bl and tr == br:
            builder.place_vert_wall(x, y, tl, tr)
        else:
            builder.place_pillar(x, y)


# Main entrypoint! Call this to build a level
def from_rects(width: np.uint, height: np.uint, rects):
    grid = rasterize(width, height, rects)
    level = basemap.Builder(width, height)
    apply_grid(grid, level)
    return level.get()


if __name__ == '__main__':
    seed: np.int64 = offgrid.hash64(np.int64(time.time_ns()))
    width, height = np.uint(80), np.uint(50)
    #width, height = np.uint(50), np.uint(25)
    box_size = np.uint(8)
    # generate offset grid rectangles which will cover the game area
    rects = offgrid.generate(width, height, box_size, seed, edge=0.08)
    # generate a level map & room list from these rectangles
    maze = from_rects(width, height, rects)
    # render the maze in ASCII chars for display
    text = render.to_chars(maze)

    # print the maze
    for y in range(height):
        line = ""
        for x in range(width):
            line += chr(text[x, y])
        print(line)

    # ta-da
