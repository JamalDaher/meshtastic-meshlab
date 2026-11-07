"""Compare candidate geographic nodes using ideal free-space link estimates."""

def rank_sites(nodes, links):
    """Rank by count of above-sensitivity peers, then weakest active margin.

    This is an illustrative graph score, not a terrain-aware site recommendation.
    """
    if not isinstance(nodes, list) or not isinstance(links, list):
        raise ValueError("nodes and links must be lists")
    names = [n["name"] for n in nodes]
    if len(set(names)) != len(names):
        raise ValueError("Node names must be unique")
    stats = {name: {"name": name, "reachable_peers": 0,
                    "below_sensitivity_peers": 0, "weakest_active_margin_db": None,
                    "mean_active_margin_db": None} for name in names}
    margins = {name: [] for name in names}
    for link in links:
        a, b = link["source"], link["target"]
        if a not in stats or b not in stats or a == b:
            raise ValueError("Link refers to invalid nodes")
        for name in (a, b):
            if link["above_sensitivity"]:
                stats[name]["reachable_peers"] += 1
                margins[name].append(float(link["link_margin_db"]))
            else:
                stats[name]["below_sensitivity_peers"] += 1
    for name in names:
        if margins[name]:
            stats[name]["weakest_active_margin_db"] = round(min(margins[name]), 2)
            stats[name]["mean_active_margin_db"] = round(sum(margins[name]) / len(margins[name]), 2)
    ranked = sorted(stats.values(), key=lambda row: (
        -row["reachable_peers"],
        -(row["weakest_active_margin_db"] if row["weakest_active_margin_db"] is not None else float("-inf")),
        row["name"]))
    for rank, row in enumerate(ranked, start=1):
        row["rank"] = rank
    return ranked
