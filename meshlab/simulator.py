"""Deterministic, offline Meshtastic-style mesh simulation."""
from dataclasses import dataclass, asdict
import math
import random

@dataclass(frozen=True)
class Node:
    node_id: str
    name: str
    x: float
    y: float
    battery: int

def make_nodes(count: int = 8, seed: int = 42) -> list[Node]:
    if not 2 <= count <= 50:
        raise ValueError("Node count must be between 2 and 50")
    rng = random.Random(seed)
    return [
        Node(f"!sim{i:04x}", f"Node {i + 1}", round(rng.uniform(0, 10), 2),
             round(rng.uniform(0, 10), 2), rng.randint(30, 100))
        for i in range(count)
    ]

def link_metrics(a: Node, b: Node, max_range: float = 5.0) -> dict | None:
    """Illustrative distance-based link model, not a real LoRa link budget."""
    distance = math.hypot(a.x - b.x, a.y - b.y)
    if distance > max_range:
        return None
    return {"source": a.node_id, "target": b.node_id,
            "distance": round(distance, 2),
            "snr": round(12 - 3 * distance, 1),
            "rssi": round(-65 - 7 * distance, 1)}

def simulate(count: int = 8, seed: int = 42, max_range: float = 5.0) -> dict:
    if max_range <= 0:
        raise ValueError("Range must be positive")
    nodes = make_nodes(count, seed)
    links = [
        metric for i, a in enumerate(nodes) for b in nodes[i + 1:]
        if (metric := link_metrics(a, b, max_range)) is not None
    ]
    return {"nodes": [asdict(node) for node in nodes], "links": links}
