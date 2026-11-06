"""Pure graph-state helpers for outage overlays."""
from meshlab.resilience import analyze_failure

def outage_overlay(data: dict, failed_nodes=()):
    failed = set(failed_nodes)
    state = analyze_failure(data, failed)
    active_links = [link for link in data["links"]
                    if link["source"] not in failed and link["target"] not in failed]
    return {"offline_nodes": sorted(failed),
            "online_nodes": sorted(n["node_id"] for n in data["nodes"] if n["node_id"] not in failed),
            "active_links": active_links,
            "state": state}
