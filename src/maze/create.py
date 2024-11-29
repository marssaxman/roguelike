
import numpy as np
from . import offgrid
from . import basemap
from . import connect

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
        # Skip rects whose width or height is less than 2, because they would
        # be filled with walls and therefore impassable
        if (right-left) < 2 or (bottom - top) < 2:
            continue
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

def level(width, height, rng) -> basemap.BaseMap:
    """Generate a basemap for a level having the specified dimensions."""
    # Generate offset grid rectangles which will cover the game area.
    grid_seed = offgrid.hash64(rng.integers(0xFFFFFFFF))
    rects = offgrid.generate(
        width=np.uint(width),
        height=np.uint(height),
        box_size=np.uint(8),
        seed=np.int64(grid_seed),
        edge=0.08
    )
    grid = rasterize(width, height, rects)
    builder = basemap.Builder(width, height)
    apply_grid(grid, builder)
    # The grid squares have become isolated rooms, separated by walls.
    # Connect these rooms into a playable maze.
    connect.fully(builder=builder, rng=rng)
    connect.some(builder=builder, rng=rng)
    connect.corridors(builder=builder)
    return builder.build()

