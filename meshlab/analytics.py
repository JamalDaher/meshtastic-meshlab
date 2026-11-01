"""Privacy-preserving analysis of bounded packet metadata."""
import csv
import io
from datetime import datetime, timezone, timedelta

FIELDS = ("time", "node", "snr", "rssi")

def signal_series(events, node=None):
    rows = [{key: e.get(key) for key in FIELDS} for e in events
            if node is None or e.get("node") == node]
    return sorted(rows, key=lambda e: e["time"] or "")

def node_activity(events, now=None, minutes=5):
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=minutes)
    latest, counts = {}, {}
    for event in events:
        node = event.get("node")
        if not node:
            continue
        counts[node] = counts.get(node, 0) + 1
        try:
            timestamp = datetime.fromisoformat(event["time"])
            if timestamp.tzinfo is None:
                continue
        except (ValueError, TypeError, KeyError):
            continue
        if node not in latest or timestamp > latest[node]:
            latest[node] = timestamp
    return [{"node": node, "packets": count,
             "last_seen": latest[node].isoformat() if node in latest else None,
             "active": node in latest and latest[node] >= cutoff}
            for node, count in sorted(counts.items())]

def export_csv(events):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDS, extrasaction="ignore")
    writer.writeheader()
    for event in events:
        row = {key: event.get(key) for key in FIELDS}
        for key in ("node", "time"):
            value = row[key]
            if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
                row[key] = "'" + value
        writer.writerow(row)
    return output.getvalue()
