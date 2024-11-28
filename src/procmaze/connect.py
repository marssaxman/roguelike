

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
        wall = builder.wall_between(joint_a, joint_b)
        x, y = rng.choice(list(wall.tiles()))
        builder.open_door(x, y, joint_a, joint_b)
        # Absorb both neighboring connected sets into the work set.
        collect_connections(builder, joint_a, katamari)
        collect_connections(builder, joint_b, katamari)
        other_ids -= katamari

