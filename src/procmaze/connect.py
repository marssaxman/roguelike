

def collect_connections(builder, room_id, katamari=set()):
    if room_id in katamari:
        return katamari
    katamari.add(room_id)
    room = builder.room(room_id)
    for conex in room.connection_ids():
        collect_connections(builder, conex, katamari)
    return katamari


def disconnected_neighbors(builder, katamari):
    for room_id in katamari:
        room = builder.room(room_id)
        for n_id in room.neighbor_ids():
            if n_id in katamari:
                continue
            yield (room_id, n_id)


def open_random_door(builder, a, b, rng):
    wall = builder.wall_between(a, b)
    x, y = rng.choice(list(wall.tiles()))
    builder.open_door(x, y, a, b)


#intentional entrypoint
def fully(builder, rng):
    """Ensure that every room is reachable from every other room."""
    # Pick a room at random.
    other_ids = set(builder.room_ids())
    start_id = rng.choice(list(builder.room_ids()))
    katamari = collect_connections(builder, start_id)
    other_ids -= katamari
    while other_ids:
        options = list(disconnected_neighbors(builder, katamari))
        # Pick a connection at random. Open a random spot in its wall.
        joint_a, joint_b = rng.choice(options)
        open_random_door(builder, joint_a, joint_b, rng)
        # Absorb both neighboring connected sets into the work set.
        collect_connections(builder, joint_a, katamari)
        collect_connections(builder, joint_b, katamari)
        other_ids -= katamari


def some(builder, rng):
    """Add some connections between disconnected rooms."""
    # Pick a randomly distributed number of rooms between 1/4 and 3/4.
    # Randomly select that many rooms. For each of these rooms, if it has
    # any disconnected neighbors, pick one of them randomly and connect.
    room_ids = list(builder.room_ids())
    room_count = len(room_ids)
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
        open_random_door(builder, r_id, other_id, rng)

