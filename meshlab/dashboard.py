"""Compact, deterministic connectivity summary for MeshLab simulations."""
from meshlab.outage_overlay import outage_overlay
from meshlab.weak_points import weak_points

def simulation_dashboard(data, failed_nodes=()):
    overlay = outage_overlay(data, failed_nodes)
    state = overlay["state"]
    weak = weak_points(data)
    total = len(data["nodes"])
    online = len(overlay["online_nodes"])
    return {
        "total_nodes": total,
        "online_nodes": online,
        "offline_nodes": total - online,
        "active_links": len(overlay["active_links"]),
        "connected_groups": state["components"],
        "largest_group": state["largest_component"],
        "largest_group_pct": round(100 * state["largest_component"] / online, 1) if online else 0.0,
        "critical_nodes": weak["critical_node_count"],
        "bridge_links": weak["bridge_link_count"],
    }
