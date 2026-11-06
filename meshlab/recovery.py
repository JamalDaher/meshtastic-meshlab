"""Greedy node restoration ranking for synthetic connectivity graphs."""
from meshlab.resilience import analyze_failure

def recovery_options(data: dict, failed_nodes=()):
    failed = set(failed_nodes)
    current = analyze_failure(data, failed)
    options = []
    for node_id in sorted(failed):
        after = analyze_failure(data, failed - {node_id})
        options.append({
            "node_id": node_id,
            "groups_after": after["components"],
            "groups_reduced": current["components"] - after["components"],
            "largest_group_after": after["largest_component"],
            "largest_group_gain": after["largest_component"] - current["largest_component"],
            "links_restored": after["remaining_links"] - current["remaining_links"],
        })
    return sorted(options, key=lambda row: (-row["largest_group_gain"],
                                            -row["groups_reduced"],
                                            -row["links_restored"], row["node_id"]))

def recovery_sequence(data: dict, failed_nodes=()):
    remaining = set(failed_nodes)
    analyze_failure(data, remaining)  # validate IDs even if no candidates
    result = []
    while remaining:
        best = recovery_options(data, remaining)[0]
        result.append({"step": len(result) + 1, **best})
        remaining.remove(best["node_id"])
    return result
