"""Observed RSSI/SNR summaries, not inferred link quality or delivery rates."""
import math
from statistics import mean

def signal_quality_summary(events, max_samples=200):
    """Summarize finite receive metadata per node from bounded recent history."""
    groups = {}
    for event in events[:max_samples]:
        node = event.get("node")
        if not isinstance(node, str) or not node:
            continue
        group = groups.setdefault(node, {"snr": [], "rssi": [], "packets": 0})
        group["packets"] += 1
        for field in ("snr", "rssi"):
            value = event.get(field)
            if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
                group[field].append(float(value))
    rows = []
    for node, group in sorted(groups.items()):
        snr, rssi = group["snr"], group["rssi"]
        rows.append({
            "node": node, "observed_packets": group["packets"],
            "snr_samples": len(snr), "mean_snr_db": round(mean(snr), 2) if snr else None,
            "minimum_snr_db": min(snr) if snr else None,
            "maximum_snr_db": max(snr) if snr else None,
            "rssi_samples": len(rssi), "mean_rssi_dbm": round(mean(rssi), 2) if rssi else None,
            "minimum_rssi_dbm": min(rssi) if rssi else None,
            "maximum_rssi_dbm": max(rssi) if rssi else None,
        })
    return rows
