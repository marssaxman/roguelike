
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


def _rasterize(width: np.uint, height: np.uint, rects):
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


def _apply_grid(grid, builder):
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
    width: np.uint,
    height: np.uint,
    box_size: np.uint = np.uint(8), # minimum 3
    rng: np.random.Generator = np.random.default_rng(),
) -> basemap.BaseMap:
    """Generate a basemap for a level having the specified dimensions."""
    # Generate offset grid rectangles which will cover the game area.
    # We will use half the requested width and height, ensuring that every
    # rect has a minimum dimension 2, which we need in order to line each
    # edge of the room with a wall tile.
    assert box_size > 2
    grid_seed = offgrid.hash64(rng.integers(0xFFFFFFFF))
    rects = _coarse_grid(
        width=width,
        height=height,
        box_size=box_size,
        seed=np.int64(grid_seed),
        edge=0.15
    )
    assert rects
    grid = _rasterize(width, height, rects)
    builder = basemap.Builder(width, height)
    _apply_grid(grid, builder)
    # The grid squares have become isolated rooms, separated by walls.
    # Connect these rooms into a playable maze.
    connect.fully(builder=builder, rng=rng)
    connect.some(builder=builder, rng=rng)
    connect.corridors(builder=builder)
    return builder.build()


def _mask_rects(rects, mask):
    """Return each rect which intersects any nonzero element of the mask."""
    for left, top, right, bottom in rects:
        left = np.int(max(left, 0))
        top = np.int(max(top, 0))
        right = np.int(min(right, mask.shape[0]))
        bottom = np.int(min(bottom, mask.shape[1]))
        if np.any(mask[left:right, top:bottom]):
            yield left, top, right, bottom

def _lair_mask(width, height):
    # The topmost floor contains the Lair of Bob, which must cover at least
    # the centermost 8x8 tiles of the game map.
    # Allocate one extra row and column for compatibility with _rasterize
    center_x = np.floor_divide(width, 2, dtype=np.uint)
    center_y = np.floor_divide(height, 2, dtype=np.uint)
    mask_l = np.subtract(center_x, 4, dtype=np.uint)
    mask_r = np.add(center_x, 4, dtype=np.uint)
    mask_t = np.subtract(center_y, 4, dtype=np.uint)
    mask_b = np.add(center_y, 4, dtype=np.uint)
    assert mask_l >= 0 and mask_t >= 0
    assert mask_r <= width and mask_b <= height
    return _rasterize(width, height, [(mask_l, mask_t, mask_r, mask_b)])


def tower(
    width: np.uint,
    height: np.uint,
    stories: np.uint, # minimum 1
    box_size: np.uint = np.uint(8), # minimum 3
    rng: np.random.Generator = np.random.default_rng(),
) -> List[basemap.BaseMap]:

    # Initial mask: centered area large enough for Lair of Bob
    mask = _lair_mask(width, height)
    # Populate a list of maps, from top down (?)
    maps = list()
    for level in range(stories):
        grid_seed = offgrid.hash64(rng.integers(0xFFFFFFFF))
        rects = _coarse_grid(
            width=width,
            height=height,
            box_size=6,
            seed=np.int64(grid_seed),
            edge=0.075
        )
        assert rects
        grid = _rasterize(width, height, _mask_rects(rects, mask))
        builder = basemap.Builder(width, height)
        _apply_grid(grid, builder)
        connect.fully(builder=builder, rng=rng)
        connect.some(builder=builder, rng=rng)
        connect.corridors(builder=builder)
        maps.append(builder.build())
        mask += grid
    return maps
