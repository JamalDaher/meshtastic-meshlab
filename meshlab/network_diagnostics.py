"""Descriptive receive-data diagnostics; no RF delivery claims."""
from meshlab.live_dashboard import live_node_summary
from meshlab.signal_quality import signal_quality_summary

def diagnostic_rows(events, now=None, minimum_packets=3):
    nodes = live_node_summary(events, now=now)
    signals = {r["node"]: r for r in signal_quality_summary(events)}
    rows = []
    for node in nodes:
        quality = signals.get(node["node"], {})
        flags = []
        if not node["active_last_5_min"]:
            flags.append("No recent packets")
        if node["packets_observed"] < minimum_packets:
            flags.append("Few observed packets")
        if not quality.get("snr_samples"):
            flags.append("No SNR readings")
        if not quality.get("rssi_samples"):
            flags.append("No RSSI readings")
        rows.append({
            "node": node["node"],
            "observed_packets": node["packets_observed"],
            "last_seen_utc": node["last_seen_utc"],
            "diagnostic_flags": "; ".join(flags) if flags else "No receive-data gaps flagged",
            "flags_count": len(flags),
        })
    return sorted(rows, key=lambda r: (-r["flags_count"], r["node"]))

def diagnostic_totals(rows):
    return {
        "observed_nodes": len(rows),
        "nodes_with_flags": sum(row["flags_count"] > 0 for row in rows),
        "nodes_without_flags": sum(row["flags_count"] == 0 for row in rows),
    }
