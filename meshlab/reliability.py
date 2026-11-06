"""Exact single-node outage sensitivity for synthetic mesh graphs."""
from meshlab.resilience import analyze_failure

def single_node_impact(data: dict) -> list[dict]:
    """Evaluate each possible single-node outage; sorted by fragmentation impact."""
    baseline = analyze_failure(data)
    rows = []
    for node in data["nodes"]:
        node_id = node["node_id"]
        state = analyze_failure(data, [node_id])
        rows.append({
            "node_id": node_id,
            "name": node.get("name", node_id),
            "components_after": state["components"],
            "component_change": state["components"] - baseline["components"],
            "largest_group_after": state["largest_component"],
            "links_remaining": state["remaining_links"],
        })
    return sorted(rows, key=lambda r: (-r["component_change"], r["largest_group_after"], r["node_id"]))

def range_comparison(count: int, seed: int, ranges: list[float]) -> list[dict]:
    """Compare synthetic topology connectivity at the same node locations."""
    from meshlab.simulator import simulate
    if not ranges or any(r <= 0 for r in ranges):
        raise ValueError("ranges must contain positive values")
    rows = []
    for radius in ranges:
        data = simulate(count=count, seed=seed, max_range=radius)
        baseline = analyze_failure(data)
        impact = single_node_impact(data)
        rows.append({
            "range": radius,
            "links": baseline["remaining_links"],
            "connected_groups": baseline["components"],
            "critical_nodes": sum(row["component_change"] > 0 for row in impact),
            "worst_components_after_one_failure": max(
                (row["components_after"] for row in impact), default=0),
        })
    return rows
