
import numpy as np
from typing import List, Tuple
from . import offgrid
from . import basemap
from . import connect


def _grid_seed(rng):
    return offgrid.hash64(rng.integers(0xFFFFFFFF))


def _coarse_grid(
    shape: Tuple[np.uint, np.uint],
    box_size: np.uint,
    seed: np.int64,
    edge: float, # range 0..0.5, controls irregularity of grid
):
    """Generate an offset grid using half the target resolution."""
    width = shape[0]
    height = shape[1]
    for left, top, right, bottom in offgrid.generate(
        width=np.floor_divide(np.uint(width), 2, dtype=np.uint),
        height=np.floor_divide(np.uint(height), 2, dtype=np.uint),
        box_size=np.floor_divide(np.uint(box_size+1), 2, dtype=np.uint),
        seed=seed,
        edge=np.double(edge),
    ):
        yield left * 2, top * 2, right * 2, bottom * 2


def _rasterize(rects, grid):
    # Allocate an extra row and column, which will be left empty;
    # this means we can skip the range checks when scanning 2x2 boxes.
    width = grid.shape[0]
    height = grid.shape[1]
    counter = 0
    grid[:] = 0
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
    assert grid.shape[1] > builder.shape[1]
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
    shape: Tuple[int, int],
    box_size: np.uint = np.uint(8), # minimum 3
    rng: np.random.Generator = np.random.default_rng(),
) -> basemap.BaseMap:
    """Generate a basemap for a level having the specified dimensions."""
    assert box_size >= 3
    width, height = shape
    assert width >= 8 and height >= 8
    # Generate offset grid rectangles which will cover the game area.
    # We will use half the tile grid resolution, to ensure that every rect
    # has enough open area to accommodate wall tiles along its edges.
    # We will also allocate a raster grid one unit larger than the desired
    # map grid, then render into the center of this array, leaving one space
    # empty around every edge. That way we can convert each 2x2 group into
    # one map tile, overscanning the edges, to generate perimeter walls.
    grid = np.zeros((np.uint(width+1), np.uint(height+1)), dtype=np.uint)
    inset = grid[1:width, 1:height]
    grid_seed = _grid_seed(rng)
    rects = _coarse_grid(
        shape=inset.shape,
        box_size=box_size,
        seed=np.int64(grid_seed),
        edge=0.15,
    )
    assert rects
    _rasterize(rects, inset)
    builder = basemap.Builder(shape=shape)
    _apply_grid(grid, builder)
    # The grid squares have become isolated rooms, separated by walls.
    # Connect these rooms into a playable maze.
    connect.fully(builder=builder, rng=rng)
    connect.some(builder=builder, rng=rng)
    connect.corridors(builder=builder)
    return builder.build()


def _filter_rects(rects, mask):
    """Return each rect which intersects any nonzero element of the mask."""
    width = mask.shape[0]
    height = mask.shape[1]
    for left, top, right, bottom in rects:
        left = np.clip(left, 0, width)
        top = np.clip(top, 0, height)
        right = np.clip(right, 0, width)
        bottom = np.clip(bottom, 0, height)
        if right-left <= 1 or bottom-top <= 1:
            continue
        if np.any(mask[left:right, top:bottom]):
            yield left, top, right, bottom


def _make_lair_mask(grid, size=8):
    # The topmost floor contains the Lair of Bob, which must cover at least
    # the centermost NxN tiles of the game map.
    width = grid.shape[0]
    height = grid.shape[1]
    center_x = np.floor_divide(width, 2, dtype=np.uint)
    center_y = np.floor_divide(height, 2, dtype=np.uint)
    half_size = np.floor_divide(np.uint(size+1), 2, dtype=np.uint)
    mask_l = np.subtract(center_x, half_size, dtype=np.uint)
    mask_r = np.add(center_x, half_size, dtype=np.uint)
    mask_t = np.subtract(center_y, half_size, dtype=np.uint)
    mask_b = np.add(center_y, half_size, dtype=np.uint)
    assert mask_l >= 0 and mask_t >= 0
    assert mask_r <= width and mask_b <= height
    _rasterize([(mask_l, mask_t, mask_r, mask_b)], grid)


def tower(
    shape: Tuple[int, int],
    stories: np.uint, # minimum 1
    box_size: np.uint = np.uint(8), # minimum 3
    rng: np.random.Generator = np.random.default_rng(),
) -> List[basemap.BaseMap]:
    assert stories > 0
    width, height = shape
    assert width >= 8 and height >= 8
    # We will generate one level after another, reusing the same raster grid,
    # using each floor's footprint as a mask for the next, to ensure that the
    # tower only grows and never leaves an upper floor unsupported.
    grid = np.zeros((np.uint(width+1), np.uint(height+1)), dtype=np.uint)
    inset = grid[1:width, 1:height]
    mask = np.zeros_like(inset)

    # The initial mask is a centered area large enough for Lair of Bob
    _make_lair_mask(mask, size=4)
    # Lair of Bob is special: we want exactly three rooms of reasonably
    # proportional size - the antechamber, Bob's room, and the amulet room.
    # There should be exactly two doors and no corridors on this map.
    # We will set up the parameters to make this probable, then loop until
    # we get what we want.
    levels: List[basemap.BaseMap] = list()
    while not levels:
        grid_seed = _grid_seed(rng)
        # make slightly more regular rooms than normal to encourage the
        # desired layout to occur. 
        rects = _coarse_grid(
            shape=inset.shape,
            box_size=np.uint(5),
            seed=np.int64(grid_seed),
            edge=0.22,
        )
        inset[:] = 0
        _rasterize(_filter_rects(rects, mask), inset)
        builder = basemap.Builder(shape=shape)
        _apply_grid(grid, builder)
        if len(builder.room_ids()) != 3:
            continue
        if not connect.lair(builder=builder, rng=rng):
            continue
        levels.append(builder.build())

    # Generate the rest of the ziggurat.
    for level in range(1, stories):
        # Add the previous level's footprint to the mask for this level.
        mask[inset.nonzero()] = 1
        # Generate an offset grid and render it into the room grid.
        grid_seed = _grid_seed(rng)
        rects = _coarse_grid(
            shape=inset.shape,
            box_size=box_size,
            seed=np.int64(grid_seed),
            edge=0.1
        )
        # Rasterize every rectangle which overlays the required mask.
        _rasterize(_filter_rects(rects, mask), inset)
        # Build a level map from the room grid.
        builder = basemap.Builder(shape=shape)
        _apply_grid(grid, builder)
        connect.fully(builder=builder, rng=rng)
        connect.some(builder=builder, rng=rng)
        connect.corridors(builder=builder)
        levels.append(builder.build())
        connect.floors(levels[level-1], levels[level], rng)

    # We generate floors from the top down, appending each one as we create
    # it, but we want to start the game on the bottom floor and move upward.
    levels.reverse()
    connect.entrance(levels[0], rng)
    return levels
