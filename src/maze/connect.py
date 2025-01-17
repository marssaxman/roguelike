import numpy as np
from .basemap import Tile

def _collect_connections(builder, room_id, katamari):
    if room_id in katamari:
        return katamari
    katamari.add(room_id)
    room = builder.room(room_id)
    for conex in room.connection_ids():
        _collect_connections(builder, conex, katamari)


def _disconnected_neighbors(builder, katamari):
    for room_id in katamari:
        room = builder.room(room_id)
        for n_id in room.neighbor_ids():
            if n_id in katamari:
                continue
            yield (room_id, n_id)


def _open_random_door(builder, a, b, rng):
    wall = builder.wall_between(a, b)
    x, y = rng.choice(list(wall.tiles()))
    if rng.choice([0, 1]):
        builder.open_door(x, y, a, b)
    else:
        builder.open_passage(x, y, a, b)


def fully(builder, rng):
    """Ensure that every room is reachable from every other room."""
    # Pick a room at random.
    if not builder.room_ids():
        return
    other_ids = set(builder.room_ids())
    start_id = rng.choice(list(builder.room_ids()))
    katamari = set()
    _collect_connections(builder, start_id, katamari)
    other_ids -= katamari
    while other_ids:
        options = list(_disconnected_neighbors(builder, katamari))
        # Pick a connection at random. Open a random spot in its wall.
        joint_a, joint_b = rng.choice(options)
        _open_random_door(builder, joint_a, joint_b, rng)
        # Absorb both neighboring connected sets into the work set.
        _collect_connections(builder, joint_a, katamari)
        _collect_connections(builder, joint_b, katamari)
        other_ids -= katamari


def some(builder, rng):
    """Add some connections between disconnected rooms."""
    # Pick a randomly distributed number of rooms between 1/4 and 3/4.
    # Randomly select that many rooms. For each of these rooms, if it has
    # any disconnected neighbors, pick one of them randomly and connect.
    room_ids = list(builder.room_ids())
    room_count = len(room_ids)
    if room_count < 2:
        return
    min_rooms = room_count // 4
    max_rooms = room_count - min_rooms
    link_count = rng.integers(min_rooms, max_rooms)
    linkables = rng.choice(room_ids, link_count)
    for r_id in linkables:
        room = builder.room(r_id)
        unlinked_ids = room.neighbor_ids() - room.connection_ids()
        if not unlinked_ids:
            continue
        other_id = rng.choice(list(unlinked_ids))
        _open_random_door(builder, r_id, other_id, rng)


def corridors(builder):
    """Open all one-square walls."""
    # Try to make corridors useful by opening doors at their extreme ends.
    # Find all the corridors and iterate through their single-cell walls;
    # for each one which is not already open, try to create a door.
    for room in filter(lambda x: x.is_corridor(), builder.rooms()):
        walls = builder.walls_around(room.id)
        for wall in filter(lambda x: 1 == x.area(), walls):
            if not wall.has_doorway():
                x,y = next(iter(wall.tiles()))
                builder.open_door(x, y, wall.a, wall.b)


def lair(builder, rng):
    """Connect doors in the pattern required for Bob's lair."""
    # Identify the largest room.
    # Open doors to its two adjacent rooms.
    # If there are other rooms, ignore them.
    # Return true if we were able to do this.
    biggest = None
    for room in builder.rooms():
        if room.is_corridor():
            return False
        if biggest and len(room.tiles()) < len(biggest.tiles()):
            continue
        biggest = room
    nb_ids = list(biggest.neighbor_ids())
    if len(nb_ids) < 2:
        return False
    for i in range(2):
        wall = builder.wall_between(biggest.id, nb_ids[i])
        x, y = rng.choice(list(wall.tiles()))
        builder.open_door(x, y, biggest.id, nb_ids[i])
    return True

def _adjacent_wall_count(maze):
    # For each tile, how many adjacent tiles are walls?
    walls = np.where(maze.tiles == Tile.WALL, 1, 0)
    mask = np.zeros_like(walls)
    mask[0:-1,...] += walls[1::,...]
    mask[1::,...] += walls[0:-1,...]
    mask[::, 0:-1] += walls[::, 1::]
    mask[::, 1::] += walls[::, 0:-1]
    return mask

def _stair_scores(maze):
    # Compute stair placement desirability score for each maze tile.
    # Maximum score is 4; illegal placements are scored zero.
    # Utility function for `floors`.
    # Begin with all floor tiles available.
    mask = np.where(maze.tiles == Tile.FLOOR, 1, 0)
    # Exclude passages between rooms and all their adjacent tiles, so we
    # do not block movement between rooms.
    for wall in maze.walls:
        for x,y in wall.tiles():
            mask[x,y] = 0
        if not wall.has_doorway():
            continue
        dx,dy = wall.doorway
        for y in range(max(0, dy-1), min(maze.shape[1], dy+2)):
            for x in range(max(0, dx-1), min(maze.shape[0], dx+2)):
                mask[x,y] = 0
    # Don't block narrow passageways: only their endpoints are usable.
    for room in maze.rooms:
        min_x, min_y = maze.shape
        max_x, max_y = 0, 0
        # identify the coordinate extremes
        for x, y in room.tiles():
            min_x, min_y = min(min_x, x), min(min_y, y)
            max_x, max_y = max(max_x, x), max(max_y, y)
        # this only applies to rooms where width or height == 1
        # (corridors and closets)
        if max_x != min_x and max_y != min_y:
            continue
        # block out any tiles which are not at one of the room's corners
        for x, y in room.tiles():
            if x != min_x and x != max_x:
                mask[x,y] = 0
            if y != min_y and y != max_y:
                mask[x,y] = 0
    # Having now identified all legal spots, score them: add one point for
    # each adjacent wall tile, thus preferring enclosed spaces.
    wall_bonus = _adjacent_wall_count(maze) * mask
    mask += wall_bonus
    return mask

def _traverse_connections(room, steps, distances):
    # Record this room's distance from the origin.
    if room not in distances or distances[room] > steps:
        distances[room] = steps
    else:
        return
    for connection in room.connections:
        _traverse_connections(connection, steps+1, distances)

def _room_remoteness(maze):
    """
    How many walls must one cross to reach each room?
    If the maze has an exit, we use that as a starting point.
    Otherwise, we choose the largest room.
    Why this formula? Because we expect to link the tower from the top down:
    the top floor is Bob's lair, and the largest room is Bob's room, so we
    don't want the stairs there. Each following floor will begin with its exit
    already defined; we try to put the entry somewhere remote so the player
    will organically have to explore the level before moving on to the next.
    """
    start = None
    if maze.exit:
        for room in maze.rooms:
            if maze.exit in room.tiles():
                start = room
                break
    if not start:
        for room in maze.rooms:
            if start and len(room.tiles()) < len(start.tiles()):
                continue
            start = room
    # Compute roomwise distance to each other room.
    distances = dict()
    _traverse_connections(start, 0, distances)
    return distances

def _remoteness_scores(maze):
    """
    Compute the remoteness score for each floor square in this maze.
    """
    distances = _room_remoteness(maze)
    mask = np.zeros_like(maze.tiles)
    for room, steps in distances.items():
        for x, y in room.tiles():
            mask[x, y] = steps
    return mask

def floors(above, below, rng):
    """Create a stairway linking these maps."""
    # We want the best placement which is legal for both floors.
    sites = _stair_scores(above) * _stair_scores(below)
    weights = sites * _remoteness_scores(above)
    best_weight = weights.max()
    # Pick at random from equivalent best options.
    x, y = rng.choice(np.argwhere(weights == best_weight))
    assert above.tiles[x, y] == Tile.FLOOR
    assert below.tiles[x, y] == Tile.FLOOR
    above.entry = (x, y)
    below.exit = (x, y)

def entrance(level, rng):
    """
    Place an outside entrance point in this ground-floor level.
    We want this to be a prominent, face-on door, so it must be placed in the
    perimeter wall on the top or the bottom of the tower. For gameplay reasons,
    select a random tile from the the rooms which are furthest from the exit.

    """
    # Simplifying edge cases, add an empty row above and below the tile map.
    expanded_shape = (level.shape[0], level.shape[1]+2)
    tiles = np.full(expanded_shape, Tile.VOID, dtype=level.tiles.dtype)
    tiles[::, 1:-1] = level.tiles
    # Look for wall tiles bordering the void.
    voids = np.where(tiles == Tile.VOID, 1, 0)
    walls = np.where(tiles == Tile.WALL, 1, 0)
    floors = np.where(tiles == Tile.FLOOR, 1, 0)
    upper = np.roll(voids, 1, axis=1) * walls * np.roll(floors, -1, axis=1)
    lower = np.roll(voids, -1, axis=1) * walls * np.roll(floors, 1, axis=1)
    assert not np.any(lower * upper)
    # Weight the perimeter tiles according to distance from the exit stairs.
    weights = _remoteness_scores(level)
    upper = upper[::, 1:-1] * np.roll(weights, -1, axis=1)
    lower = lower[::, 1:-1] * np.roll(weights, 1, axis=1)
    perimeter = upper + lower
    # Pick any of the furthest wall tiles, at random.
    options = list(np.transpose(np.where(perimeter == np.max(perimeter))))
    level.entry = tuple(rng.choice(options))
