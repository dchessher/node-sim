from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Tuple

from nodes import NodeGroup
from traversal import shortest_path


def compute_radial_position(
    index: int,
    total: int,
    *,
    center: Tuple[int, int] = (600, 390),
    radius: int = 240,
) -> Tuple[int, int]:
    """Compute a visually distinct position for a node on a single ring.

    Kept for backwards compatibility in tests; use ``compute_radial_layout``
    for a multi-ring, dynamically spaced layout.
    """

    if total <= 0:
        raise ValueError("Total number of nodes must be positive.")
    if index < 0 or index >= total:
        raise ValueError("Index must be within the total count of nodes.")

    center_x, center_y = center
    if total == 1 or index == 0:
        return center_x, center_y

    ring_count = total - 1
    angle = (2 * math.pi / ring_count) * (index - 1)
    x = center_x + int(radius * math.cos(angle))
    y = center_y + int(radius * math.sin(angle))
    return x, y


def _positions_on_ring(count: int, radius: int, center: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Return evenly spaced coordinates around a ring."""

    if count <= 0:
        return []

    center_x, center_y = center
    return [
        (
            center_x + int(radius * math.cos(2 * math.pi * i / count)),
            center_y + int(radius * math.sin(2 * math.pi * i / count)),
        )
        for i in range(count)
    ]


def compute_radial_layout(
    node_ids: List[str],
    *,
    center: Tuple[int, int] = (600, 390),
    min_radius: int = 120,
    ring_step: int = 110,
    min_spacing: int = 80,
) -> Dict[str, Tuple[int, int]]:
    """Return a dynamically spaced layout mapping for the provided nodes.

    Nodes are distributed across concentric rings with a minimum spacing target
    so they remain readable even as the total grows beyond a single ring's
    capacity.
    """

    if not node_ids:
        return {}

    positions: Dict[str, Tuple[int, int]] = {node_ids[0]: center}
    remaining = node_ids[1:]

    radius = min_radius
    idx = 0
    while idx < len(remaining):
        capacity = max(1, int(2 * math.pi * radius // min_spacing))
        take = min(capacity, len(remaining) - idx)
        ring_positions = _positions_on_ring(take, radius, center)
        for offset in range(take):
            node_id = remaining[idx + offset]
            positions[node_id] = ring_positions[offset]
        idx += take
        radius += ring_step

    return positions


class NodeSimulatorApp:
    """Tkinter-based visual demo for the node simulation."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Node Simulation Demo")
        self.root.minsize(1280, 940)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=(10, 6))
        style.configure("TLabel", padding=(4, 2))

        self.group = NodeGroup()
        self.positions: Dict[str, Tuple[int, int]] = {}
        self.highlight_path: List[str] = []

        main = ttk.Frame(root, padding=16)
        main.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self.canvas_width = 1200
        self.canvas_height = 780
        self.canvas_center = (self.canvas_width // 2, self.canvas_height // 2)
        self.canvas = tk.Canvas(main, width=self.canvas_width, height=self.canvas_height, bg="#fdfdfd", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        controls = ttk.Frame(main)
        controls.grid(row=0, column=1, sticky="nsew")
        controls.columnconfigure(1, weight=1)

        header = ttk.Label(controls, text="Node Controls", font=("Segoe UI", 12, "bold"))
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        ttk.Label(controls, text="Add Node ID:").grid(row=1, column=0, sticky="w")
        self.node_entry = ttk.Entry(controls)
        self.node_entry.grid(row=1, column=1, sticky="ew", pady=(0, 6))
        ttk.Button(controls, text="Add Node", command=self.add_node).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        separator1 = ttk.Separator(controls, orient="horizontal")
        separator1.grid(row=3, column=0, columnspan=2, sticky="ew", pady=8)

        ttk.Label(controls, text="Connect Nodes:").grid(row=4, column=0, columnspan=2, sticky="w")
        self.connect_a = ttk.Entry(controls)
        self.connect_a.grid(row=5, column=0, sticky="ew", pady=(0, 4))
        self.connect_b = ttk.Entry(controls)
        self.connect_b.grid(row=5, column=1, sticky="ew", pady=(0, 4))
        ttk.Button(controls, text="Connect", command=self.connect_nodes).grid(row=6, column=0, columnspan=2, sticky="ew")

        separator2 = ttk.Separator(controls, orient="horizontal")
        separator2.grid(row=7, column=0, columnspan=2, sticky="ew", pady=8)

        ttk.Label(controls, text="Highlight Path:").grid(row=8, column=0, columnspan=2, sticky="w")
        self.path_start = ttk.Entry(controls)
        self.path_start.grid(row=9, column=0, sticky="ew", pady=(0, 4))
        self.path_end = ttk.Entry(controls)
        self.path_end.grid(row=9, column=1, sticky="ew", pady=(0, 4))
        ttk.Button(controls, text="Find Path", command=self.find_and_highlight_path).grid(row=10, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        self.status_var = tk.StringVar(value="Add a few nodes to begin.")
        status = ttk.Label(main, textvariable=self.status_var, anchor="w", padding=(12, 8), relief=tk.FLAT)
        status.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        self._recalculate_positions()

    def add_node(self) -> None:
        node_id = self.node_entry.get().strip()
        if not node_id:
            self.status_var.set("Enter a node id.")
            return
        try:
            self.group.add_node(node_id)
            self._recalculate_positions()
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

    def _recalculate_positions(self) -> None:
        """Recompute layout for all nodes to keep spacing even."""

        self.positions = compute_radial_layout(
            self.group.list_nodes(),
            center=self.canvas_center,
            min_radius=120,
            ring_step=110,
            min_spacing=90,
        )

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
        color = "#eef5ff" if node_id in self.highlight_path else ("#f7f7f7" if standalone else "#ffffff")
        outline = "#2563eb" if node_id in self.highlight_path else "#4b5563"
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline=outline, width=2)
        self.canvas.create_text(x, y, text=node_id, font=("Segoe UI", 10, "bold"), fill="#111827")


def main() -> None:
    root = tk.Tk()
    app = NodeSimulatorApp(root)
    app.redraw()
    root.mainloop()


if __name__ == "__main__":
    main()
