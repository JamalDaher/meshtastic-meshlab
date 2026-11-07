"""Read-only live-node summaries from privacy-preserving packet metadata."""
from datetime import datetime, timezone

def live_node_summary(events, now=None, active_minutes=5):
    from meshlab.analytics import node_activity
    now = now or datetime.now(timezone.utc)
    activity = node_activity(events, now=now, minutes=active_minutes)
    latest = {}
    for event in events:
        node = event.get("node")
        if not node:
            continue
        try:
            when = datetime.fromisoformat(event["time"])
            if when.tzinfo is None:
                continue
            when = when.astimezone(timezone.utc)
        except (KeyError, ValueError, TypeError):
            continue
        if node not in latest or when > latest[node][0]:
            latest[node] = (when, event)
    result = []
    for row in activity:
        node = row["node"]
        current = latest.get(node)
        age = max(0, int((now - current[0]).total_seconds())) if current else None
        result.append({"node": node, "packets_observed": row["packets"],
                       "last_seen_utc": row["last_seen"],
                       "seconds_since_last_packet": age,
                       "active_last_5_min": row["active"],
                       "last_snr_db": current[1].get("snr") if current else None,
                       "last_rssi_dbm": current[1].get("rssi") if current else None})
    return sorted(result, key=lambda r: (not r["active_last_5_min"],
                                          r["seconds_since_last_packet"] if r["seconds_since_last_packet"] is not None else float("inf"),
                                          r["node"]))
