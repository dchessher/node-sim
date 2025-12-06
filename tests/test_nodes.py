import pytest

from nodes import NodeGroup
from traversal import breadth_first_search, shortest_path


def setup_group():
    group = NodeGroup()
    for node_id in ["A", "B", "C", "D"]:
        group.add_node(node_id)
    group.connect("A", "B")
    group.connect("B", "C")
    return group


def test_add_and_get_node():
    group = NodeGroup()
    group.add_node("X", metadata={"label": "test"})
    node = group.get_node("X")
    assert node is not None
    assert node.metadata == {"label": "test"}


def test_duplicate_node_raises():
    group = NodeGroup()
    group.add_node("X")
    with pytest.raises(ValueError):
        group.add_node("X")


def test_connect_and_neighbors():
    group = setup_group()
    assert group.get_neighbors("A") == {"B"}
    assert group.get_neighbors("B") == {"A", "C"}


def test_disconnect():
    group = setup_group()
    group.disconnect("A", "B")
    assert group.get_neighbors("A") == set()
    assert group.get_neighbors("B") == {"C"}


def test_remove_node_cleans_connections():
    group = setup_group()
    group.remove_node("B")
    assert "B" not in group.list_nodes()
    assert group.get_neighbors("A") == set()
    assert group.get_neighbors("C") == set()


def test_standalone_nodes():
    group = setup_group()
    group.add_node("E")
    assert group.get_standalone_nodes() == {"D", "E"}


def test_is_connected_and_path():
    group = setup_group()
    assert group.is_connected("A", "C") is True
    assert group.find_path("A", "C") in (["A", "B", "C"], ["A", "B", "C"])  # order check not strict
    assert group.is_connected("A", "D") is False


def test_breadth_first_search_and_shortest_path():
    group = setup_group()
    bfs_order = list(breadth_first_search(group, "A"))
    assert bfs_order[0] == "A"
    assert "C" in bfs_order
    assert shortest_path(group, "A", "C") == ["A", "B", "C"]


def test_connected_components():
    group = setup_group()
    group.add_node("X")
    components = group.connected_components()
    assert {"A", "B", "C"} in components
    assert {"D"} in components
    assert {"X"} in components
