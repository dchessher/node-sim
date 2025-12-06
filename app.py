from __future__ import annotations

import math
import tkinter as tk
from typing import Dict, List, Tuple

from nodes import NodeGroup
from traversal import shortest_path


class NodeSimulatorApp:
    """Tkinter-based visual demo for the node simulation."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Node Simulation Demo")
        self.group = NodeGroup()
        self.positions: Dict[str, Tuple[int, int]] = {}
        self.highlight_path: List[str] = []

        self.canvas = tk.Canvas(root, width=720, height=520, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        tk.Label(root, text="Add Node ID:").grid(row=1, column=0, sticky="e")
        self.node_entry = tk.Entry(root)
        self.node_entry.grid(row=1, column=1, sticky="w")
        tk.Button(root, text="Add Node", command=self.add_node).grid(row=1, column=2, padx=5, pady=5)

        tk.Label(root, text="Connect A:").grid(row=2, column=0, sticky="e")
        self.connect_a = tk.Entry(root, width=8)
        self.connect_a.grid(row=2, column=1, sticky="w")
        tk.Label(root, text="B:").grid(row=2, column=1)
        self.connect_b = tk.Entry(root, width=8)
        self.connect_b.grid(row=2, column=2, sticky="w")
        tk.Button(root, text="Connect", command=self.connect_nodes).grid(row=2, column=3, padx=5)

        tk.Label(root, text="Path from:").grid(row=3, column=0, sticky="e")
        self.path_start = tk.Entry(root, width=8)
        self.path_start.grid(row=3, column=1, sticky="w")
        tk.Label(root, text="to:").grid(row=3, column=1)
        self.path_end = tk.Entry(root, width=8)
        self.path_end.grid(row=3, column=2, sticky="w")
        tk.Button(root, text="Highlight Path", command=self.find_and_highlight_path).grid(row=3, column=3, padx=5, pady=5)

        self.status_var = tk.StringVar(value="Add a few nodes to begin.")
        tk.Label(root, textvariable=self.status_var, anchor="w").grid(row=4, column=0, columnspan=4, sticky="we", padx=10, pady=5)

    def add_node(self) -> None:
        node_id = self.node_entry.get().strip()
        if not node_id:
            self.status_var.set("Enter a node id.")
            return
        try:
            self.group.add_node(node_id)
            self.positions[node_id] = self._next_position(len(self.positions))
            self.status_var.set(f"Added node {node_id}.")
        except ValueError as exc:
            self.status_var.set(str(exc))
        self.node_entry.delete(0, tk.END)
        self.highlight_path = []
        self.redraw()

    def connect_nodes(self) -> None:
        a = self.connect_a.get().strip()
        b = self.connect_b.get().strip()
        if not a or not b:
            self.status_var.set("Provide both node ids to connect.")
            return
        try:
            self.group.connect(a, b)
            self.status_var.set(f"Connected {a} and {b}.")
        except (KeyError, ValueError) as exc:
            self.status_var.set(str(exc))
        self.connect_a.delete(0, tk.END)
        self.connect_b.delete(0, tk.END)
        self.highlight_path = []
        self.redraw()

    def find_and_highlight_path(self) -> None:
        start = self.path_start.get().strip()
        end = self.path_end.get().strip()
        if not start or not end:
            self.status_var.set("Enter start and end nodes.")
            return
        path = shortest_path(self.group, start, end)
        if path:
            self.highlight_path = path
            self.status_var.set(f"Path found: {' -> '.join(path)}")
        else:
            self.highlight_path = []
            self.status_var.set("No path found (or nodes missing).")
        self.redraw()

    def _next_position(self, index: int) -> Tuple[int, int]:
        radius = 200
        center_x, center_y = 360, 260
        if index == 0:
            return center_x, center_y
        angle = (2 * math.pi / max(1, len(self.positions))) * index
        x = center_x + int(radius * math.cos(angle))
        y = center_y + int(radius * math.sin(angle))
        return x, y

    def redraw(self) -> None:
        self.canvas.delete("all")
        edges = self.group.get_edges()
        for a, b in edges:
            color = "#666"
            if self._edge_on_path(a, b):
                color = "#2196f3"
            self._draw_edge(a, b, color)
        for node_id in self.group.list_nodes():
            self._draw_node(node_id)

    def _edge_on_path(self, a: str, b: str) -> bool:
        for idx in range(len(self.highlight_path) - 1):
            path_a, path_b = self.highlight_path[idx], self.highlight_path[idx + 1]
            if {a, b} == {path_a, path_b}:
                return True
        return False

    def _draw_edge(self, a: str, b: str, color: str) -> None:
        pos_a = self.positions.get(a)
        pos_b = self.positions.get(b)
        if not pos_a or not pos_b:
            return
        self.canvas.create_line(pos_a[0], pos_a[1], pos_b[0], pos_b[1], fill=color, width=2)

    def _draw_node(self, node_id: str) -> None:
        x, y = self.positions.get(node_id, (50, 50))
        radius = 18
        standalone = node_id in self.group.get_standalone_nodes()
        color = "#f5f5f5" if standalone else "#ffffff"
        outline = "#4caf50" if node_id in self.highlight_path else "#333"
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline=outline, width=2)
        self.canvas.create_text(x, y, text=node_id)


def main() -> None:
    root = tk.Tk()
    app = NodeSimulatorApp(root)
    app.redraw()
    root.mainloop()


if __name__ == "__main__":
    main()
