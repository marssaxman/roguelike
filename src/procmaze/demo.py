#!/usr/bin/env python3

import numpy as np
import offgrid
import time
import render
import basemap
import connect

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


def remove_empty_rooms(builder):
    # Find all the empty rooms, then delete the list. We don't want to
    # confuse the path-finding algorithm with spurious rooms which cannot
    # be traversed.
    empty_rooms = []
    for room in builder.rooms():
        if room.is_empty():
            empty_rooms.append(room.id)
    for id in empty_rooms:
        builder.delete_room(id)

def print_maze(maze):
    text = render.to_chars(maze)
    for y in range(maze.shape[1]):
        line = ""
        for x in range(maze.shape[0]):
            line += chr(text[x, y])
        print(line)


if __name__ == '__main__':
    # Everything descends from the random seed; we'll use the current time.
    seed: np.int64 = offgrid.hash64(np.int64(time.time_ns()))
    rng = np.random.default_rng(seed=np.uint(seed))

    try:
        # How big a game board do we want to build, and how big should the
        # average room be?
        width, height = np.uint(80), np.uint(50)
        box_size = np.uint(8)

        # Generate offset grid rectangles which will cover the game area.
        # Populate a basemap from those rectangles, generating rooms and walls.
        rects = offgrid.generate(width, height, box_size, seed, edge=0.08)
        grid = rasterize(width, height, rects)
        builder = basemap.Builder(width, height)
        apply_grid(grid, builder)
        # The grid squares have become isolated rooms, separated by walls.
        # Connect these rooms into a playable maze.
        remove_empty_rooms(builder)
        connect.fully(builder=builder, rng=rng)
        connect.some(builder=builder, rng=rng)
        connect.corridors(builder)
        maze = builder.get_tiles()
    except:
        print(f"starting seed: {seed}")
        raise

    # ta-da
    print_maze(maze)

