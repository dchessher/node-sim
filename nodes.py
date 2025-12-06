from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set


@dataclass
class Node:
    """Represents a node in the simulation graph."""

    id: str
    metadata: Optional[Dict[str, object]] = None
    neighbors: Set[str] = field(default_factory=set)

    def add_neighbor(self, neighbor_id: str) -> None:
        """Add a neighbor to this node's adjacency set."""
        if neighbor_id == self.id:
            raise ValueError("A node cannot connect to itself.")
        self.neighbors.add(neighbor_id)

    def remove_neighbor(self, neighbor_id: str) -> None:
        """Remove a neighbor if present."""
        self.neighbors.discard(neighbor_id)

    def get_neighbors(self) -> Set[str]:
        """Return a copy of neighbor identifiers."""
        return set(self.neighbors)


class NodeGroup:
    """Manages a collection of nodes and their relationships."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}

    def add_node(self, node_id: str, metadata: Optional[Dict[str, object]] = None) -> Node:
        if node_id in self.nodes:
            raise ValueError(f"Node '{node_id}' already exists")
        node = Node(id=node_id, metadata=metadata)
        self.nodes[node_id] = node
        return node

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def remove_node(self, node_id: str) -> None:
        node = self.nodes.pop(node_id, None)
        if node is None:
            return
        for other in self.nodes.values():
            other.remove_neighbor(node_id)

    def list_nodes(self) -> List[str]:
        return list(self.nodes.keys())

    def connect(self, a: str, b: str) -> None:
        if a == b:
            raise ValueError("Cannot create a self-connection")
        if a not in self.nodes or b not in self.nodes:
            raise KeyError("Both nodes must exist to create a connection")
        self.nodes[a].add_neighbor(b)
        self.nodes[b].add_neighbor(a)

    def disconnect(self, a: str, b: str) -> None:
        if a not in self.nodes or b not in self.nodes:
            return
        self.nodes[a].remove_neighbor(b)
        self.nodes[b].remove_neighbor(a)

    def get_neighbors(self, node_id: str) -> Set[str]:
        node = self.nodes.get(node_id)
        if node is None:
            raise KeyError(f"Node '{node_id}' not found")
        return node.get_neighbors()

    def get_edges(self) -> Set[tuple[str, str]]:
        edges: Set[tuple[str, str]] = set()
        for node_id, node in self.nodes.items():
            for neighbor in node.neighbors:
                edge = tuple(sorted((node_id, neighbor)))
                edges.add(edge)
        return edges

    def get_standalone_nodes(self) -> Set[str]:
        return {node_id for node_id, node in self.nodes.items() if not node.neighbors}

    def _traverse(self, start_id: str) -> Iterable[str]:
        visited: Set[str] = set()
        stack: List[str] = [start_id]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            yield current
            stack.extend(self.nodes[current].neighbors - visited)

    def is_connected(self, a: str, b: str) -> bool:
        if a not in self.nodes or b not in self.nodes:
            return False
        for node_id in self._traverse(a):
            if node_id == b:
                return True
        return False

    def find_path(self, start_id: str, end_id: str) -> List[str]:
        if start_id not in self.nodes or end_id not in self.nodes:
            return []
        queue: List[List[str]] = [[start_id]]
        visited: Set[str] = {start_id}
        while queue:
            path = queue.pop(0)
            node_id = path[-1]
            if node_id == end_id:
                return path
            for neighbor in self.nodes[node_id].neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return []

    def connected_components(self) -> List[Set[str]]:
        components: List[Set[str]] = []
        visited: Set[str] = set()
        for node_id in self.nodes:
            if node_id in visited:
                continue
            component: Set[str] = set()
            for member in self._traverse(node_id):
                component.add(member)
                visited.add(member)
            components.append(component)
        return components
