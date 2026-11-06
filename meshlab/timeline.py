"""Reproducible synthetic network event timelines; no hardware packets."""
import random
from meshlab.resilience import analyze_failure

def generate_timeline(data, seed=42, steps=20):
    if not 1 <= steps <= 200:
        raise ValueError("steps must be between 1 and 200")
    rng = random.Random(seed)
    ids = sorted(node["node_id"] for node in data["nodes"])
    offline = set()
    events = []
    for tick in range(steps):
        node = rng.choice(ids)
        if node in offline:
            offline.remove(node)
            action = "restored"
        else:
            offline.add(node)
            action = "offline"
        state = analyze_failure(data, offline)
        events.append({"step": tick + 1, "node": node, "event": action,
                       "offline_count": len(offline),
                       "active_nodes": state["remaining_nodes"],
                       "active_links": state["remaining_links"],
                       "connected_groups": state["components"],
                       "largest_group": state["largest_component"]})
    return events
