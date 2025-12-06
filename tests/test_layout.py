from app import compute_radial_position


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
