"""Privacy-preserving, multi-node received signal history."""
from datetime import datetime, timezone
import math

def comparison_series(events, selected_nodes=None, metric="snr", max_points=200):
    if metric not in {"snr", "rssi"}:
        raise ValueError("Metric must be snr or rssi")
    selected = set(selected_nodes) if selected_nodes is not None else None
    rows = []
    for event in events:
        node = event.get("node")
        if not isinstance(node, str) or not node or (selected is not None and node not in selected):
            continue
        value = event.get(metric)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            continue
        try:
            when = datetime.fromisoformat(event["time"])
            if when.tzinfo is None:
                continue
        except (KeyError, TypeError, ValueError):
            continue
        rows.append({"time": when.astimezone(timezone.utc).isoformat(),
                     "node": node, "reading": float(value)})
    rows.sort(key=lambda row: row["time"])
    return rows[-max_points:] if max_points > 0 else []
