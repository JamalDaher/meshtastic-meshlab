"""Conservative rankings from evaluated terrain links only."""

def rank_terrain_sites(nodes, links, comparison_rows):
    """Count verified-at-samples links; never treat unevaluated as clear."""
    by_name = {n["name"]: {"name": n["name"], "evaluated_links": 0,
                            "terrain_and_fresnel_clear": 0,
                            "terrain_blocked_or_fresnel_insufficient": 0,
                            "not_evaluated_links": 0,
                            "rf_and_terrain_clear": 0} for n in nodes}
    lookup = {frozenset((r["source"], r["target"])): r for r in comparison_rows}
    for link in links:
        pair = frozenset((link["source"], link["target"]))
        row = lookup.get(pair)
        if row is None:
            raise ValueError("Missing comparison row")
        for name in pair:
            stats = by_name[name]
            if row["terrain_status"] in ("Not evaluated", "Invalid saved profile"):
                stats["not_evaluated_links"] += 1
            else:
                stats["evaluated_links"] += 1
                if row["terrain_status"] == "Clear" and row["fresnel_status"] == "Clear":
                    stats["terrain_and_fresnel_clear"] += 1
                    if link["above_sensitivity"]:
                        stats["rf_and_terrain_clear"] += 1
                else:
                    stats["terrain_blocked_or_fresnel_insufficient"] += 1
    ranked = sorted(by_name.values(), key=lambda x: (-x["rf_and_terrain_clear"],
        -x["evaluated_links"], x["not_evaluated_links"], x["name"]))
    for rank, row in enumerate(ranked, 1):
        row["rank"] = rank
    return ranked
