"""Deterministic what-if resilience analysis for synthetic mesh topologies."""
from meshlab.topology import build_graph
import networkx as nx

def analyze_failure(data: dict, failed_nodes=()):
    """Compare connected components before/after selected node removals.

    This is graph connectivity, not Meshtastic protocol delivery simulation.
    """
    graph = build_graph(data)
    failed = set(failed_nodes)
    unknown = failed.difference(graph.nodes)
    if unknown:
        raise ValueError("Unknown node ID(s): " + ", ".join(sorted(map(str, unknown))))
    remaining = graph.copy()
    remaining.remove_nodes_from(failed)
    components = [sorted(component) for component in nx.connected_components(remaining)]
    components.sort(key=lambda c: (-len(c), c))
    return {
        "baseline_components": nx.number_connected_components(graph),
        "remaining_nodes": remaining.number_of_nodes(),
        "remaining_links": remaining.number_of_edges(),
        "components": len(components),
        "largest_component": len(components[0]) if components else 0,
        "groups": components,
    }

def critical_nodes(data: dict):
    """Find nodes whose removal increases connected-component count."""
    graph = build_graph(data)
    return sorted(nx.articulation_points(graph))
