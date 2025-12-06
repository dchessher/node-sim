from app import compute_radial_layout, compute_radial_position


def test_positions_do_not_overlap_for_first_three_nodes():
    total = 3
    positions = [compute_radial_position(i, total) for i in range(total)]
    assert len(set(positions)) == total
    # First node stays in the center
    assert positions[0] == (360, 260)


def test_position_validation():
    # Invalid total
    try:
        compute_radial_position(0, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for non-positive total")

    # Invalid index
    try:
        compute_radial_position(-1, 1)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for negative index")

    try:
        compute_radial_position(2, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for index >= total")


def test_layout_rescales_as_nodes_grow():
    node_ids = [str(i) for i in range(1, 7)]
    layout = compute_radial_layout(node_ids)

    assert len(layout) == len(node_ids)
    assert len(set(layout.values())) == len(node_ids)

    positions = list(layout.values())

    def distance(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    min_distance = min(
        distance(positions[i], positions[j])
        for i in range(len(positions))
        for j in range(i + 1, len(positions))
    )

    assert min_distance > 40, "Nodes should remain spaced apart as total grows"
