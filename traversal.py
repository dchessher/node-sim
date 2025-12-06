from __future__ import annotations

from collections import deque
from typing import Deque, Dict, Iterable, List, Optional, Set

from nodes import NodeGroup


def breadth_first_search(group: NodeGroup, start_id: str) -> Iterable[str]:
    """Yield node ids in breadth-first order starting from start_id."""
    if start_id not in group.nodes:
        return []
    visited: Set[str] = set()
    queue: Deque[str] = deque([start_id])
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        yield current
        for neighbor in sorted(group.get_neighbors(current)):
            if neighbor not in visited:
                queue.append(neighbor)


def shortest_path(group: NodeGroup, start_id: str, end_id: str) -> List[str]:
    """Return a shortest path between two nodes using BFS."""
    if start_id not in group.nodes or end_id not in group.nodes:
        return []
    queue: Deque[str] = deque([start_id])
    parents: Dict[str, Optional[str]] = {start_id: None}
    while queue:
        current = queue.popleft()
        if current == end_id:
            break
        for neighbor in group.get_neighbors(current):
            if neighbor not in parents:
                parents[neighbor] = current
                queue.append(neighbor)
    else:
        return []

    path: List[str] = []
    cursor: Optional[str] = end_id
    while cursor is not None:
        path.append(cursor)
        cursor = parents.get(cursor)
    return list(reversed(path))
