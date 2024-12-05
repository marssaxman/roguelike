
import numpy as np
from typing import List
from . import offgrid
from . import basemap
from . import connect


def _coarse_grid(
    width: np.uint,
    height: np.uint,
    box_size: np.uint,
    seed: np.int64,
    edge: np.double, # range 0..0.5, controls irregularity of grid
):
    """Generate an offset grid using half the target resolution."""
    for left, top, right, bottom in offgrid.generate(
        width=np.floor_divide(np.uint(width), 2, dtype=np.uint),
        height=np.floor_divide(np.uint(height), 2, dtype=np.uint),
        box_size=np.floor_divide(np.uint(box_size), 2, dtype=np.uint),
        seed=seed,
        edge=edge
    ):
        yield left * 2, top * 2, right * 2, bottom * 2


def _rasterize(rects, grid):
    # Allocate an extra row and column, which will be left empty;
    # this means we can skip the range checks when scanning 2x2 boxes.
    width = grid.shape[0]
    height = grid.shape[1]
    counter = 0
    for rect in rects:
        left, top, right, bottom = rect
        # Skip rects that don't lie completely within the requested area
        if left < 0 or top < 0 or right > width or bottom > height:
            continue;
        # Increment the room counter and assign it to the cell region
        counter += 1
        grid[left:right, top:bottom] = counter


def _apply_grid(grid, builder):
    """Generate map tiles from a raster grid containing room numbers."""
    # Each intersection of four grid cells yields one map tile, so we expect
    # that the grid's width and height are at least one greater than the
    # resulting map dimensions.
    assert grid.shape[0] > builder.shape[0]
    assert grid.shape[1]
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


def level(
    width: np.uint, # minimum 8
    height: np.uint, # minimum 8
    box_size: np.uint = np.uint(8), # minimum 3
    rng: np.random.Generator = np.random.default_rng(),
) -> basemap.BaseMap:
    """Generate a basemap for a level having the specified dimensions."""
    assert box_size >= 3
    assert width >= 8 and height >= 8
    # Generate offset grid rectangles which will cover the game area.
    # We will use half the tile grid resolution, to ensure that every rect
    # has enough open area to accommodate wall tiles along its edges.
    # We will also allocate a raster grid one unit larger than the desired
    # map grid, then render into the center of this array, leaving one space
    # empty around every edge. That way we can convert each 2x2 group into
    # one map tile, overscanning the edges, to generate perimeter walls.
    grid = np.zeros((np.uint(width+1), np.uint(height+1)), dtype=np.uint)
    inset = grid[1:np.uint(width-1), 1:np.uint(height-1)]
    grid_seed = offgrid.hash64(rng.integers(0xFFFFFFFF))
    rects = _coarse_grid(
        width=inset.shape[0],
        height=inset.shape[1],
        box_size=box_size,
        seed=np.int64(grid_seed),
        edge=0.15
    )
    assert rects
    _rasterize(rects, inset)
    builder = basemap.Builder(width, height)
    _apply_grid(grid, builder)
    # The grid squares have become isolated rooms, separated by walls.
    # Connect these rooms into a playable maze.
    connect.fully(builder=builder, rng=rng)
    connect.some(builder=builder, rng=rng)
    connect.corridors(builder=builder)
    return builder.build()


def _print_grid(caption, grid):
    CHARS = ".123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    print(caption)
    for y in range(grid.shape[1]):
        line = ""
        for x in range(grid.shape[0]):
            line += CHARS[grid[x, y]]
        print(line)


def _mask_rects(rects, mask):
    """Return each rect which intersects any nonzero element of the mask."""
    for left, top, right, bottom in rects:
        left = np.int(max(left, 0))
        top = np.int(max(top, 0))
        right = np.int(min(right, mask.shape[0]))
        bottom = np.int(min(bottom, mask.shape[1]))
        if np.any(mask[left:right, top:bottom]):
            yield left, top, right, bottom


def _lair_mask(grid):
    # The topmost floor contains the Lair of Bob, which must cover at least
    # the centermost 8x8 tiles of the game map.
    # Allocate one extra row and column for compatibility with _rasterize
    width = grid.shape[0]
    height = grid.shape[1]
    center_x = np.floor_divide(width, 2, dtype=np.uint)
    center_y = np.floor_divide(np.uint(height+1), 2, dtype=np.uint)
    mask_l = np.subtract(center_x, 4, dtype=np.uint)
    mask_r = np.add(center_x, 4, dtype=np.uint)
    mask_t = np.subtract(center_y, 4, dtype=np.uint)
    mask_b = np.add(center_y, 4, dtype=np.uint)
    assert mask_l >= 0 and mask_t >= 0
    assert mask_r <= width and mask_b <= height
    _rasterize([(mask_l, mask_t, mask_r, mask_b)], grid)


def tower(
    width: np.uint,
    height: np.uint,
    stories: np.uint, # minimum 1
    box_size: np.uint = np.uint(8), # minimum 3
    rng: np.random.Generator = np.random.default_rng(),
) -> List[basemap.BaseMap]:

    # Initial mask: centered area large enough for Lair of Bob
    mask = np.zeros((np.uint(width+1), np.uint(height+1)), dtype=np.uint)
    _lair_mask(mask)
    _print_grid("Initial mask", mask)
    # Populate a list of maps, from top down (?)
    maps = list()
    for level in range(stories):
        # prepare the buffer we will write the new level into
        grid = np.zeros_like(mask)
        inset = grid[1:np.uint(width-1), 1:np.uint(height-1)]
        # generate an offset grid
        grid_seed = offgrid.hash64(rng.integers(0xFFFFFFFF))
        rects = _coarse_grid(
            width=inset.shape[0],
            height=inset.shape[1],
            box_size=6,
            seed=np.int64(grid_seed),
            edge=0.075
        )
        assert rects
        _rasterize(_mask_rects(rects, mask), inset)
        _print_grid("Rasterized rooms", grid)
        builder = basemap.Builder(width, height)
        _apply_grid(grid, builder)
        connect.fully(builder=builder, rng=rng)
        connect.some(builder=builder, rng=rng)
        connect.corridors(builder=builder)
        maps.append(builder.build())
        new_mask = np.zeros_like(mask)
        new_mask[grid.nonzero()] = 1
        _print_grid("Next mask", new_mask)
        error = mask - (new_mask * mask)
        if np.any(error):
            _print_grid("Error:", error)
        mask = new_mask
    return maps
