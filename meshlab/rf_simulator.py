"""RF-derived connectivity for synthetic coordinates with an explicit km scale."""
import math
from dataclasses import asdict
from meshlab.simulator import make_nodes
from meshlab.rf import RadioProfile, link_budget

def simulate_rf(count=8, seed=42, km_per_unit=0.5, profile=None):
    """Create ideal free-space links; x/y coordinates are synthetic, not GPS."""
    if not math.isfinite(km_per_unit) or km_per_unit <= 0:
        raise ValueError("km_per_unit must be finite and positive")
    profile = profile if profile is not None else RadioProfile()
    nodes = make_nodes(count, seed)
    links = []
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            distance_km = max(math.hypot(a.x - b.x, a.y - b.y) * km_per_unit, 0.001)
            budget = link_budget(distance_km, profile)
            if budget["above_sensitivity"]:
                links.append({"source": a.node_id, "target": b.node_id,
                              "distance": round(distance_km, 3),
                              "distance_km": round(distance_km, 3),
                              "path_loss_db": budget["path_loss_db"],
                              "link_margin_db": budget["link_margin_db"],
                              "snr": None, "rssi": budget["received_power_dbm"]})
    return {"nodes": [asdict(n) for n in nodes], "links": links}
