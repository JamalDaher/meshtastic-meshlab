"""Graph-based critical node and link annotations for synthetic topology."""
import networkx as nx
from meshlab.topology import build_graph

def weak_points(data: dict) -> dict:
    graph = build_graph(data)
    critical = sorted(nx.articulation_points(graph))
    bridges = sorted(tuple(sorted(edge)) for edge in nx.bridges(graph))
    return {"critical_nodes": critical, "bridge_links": bridges,
            "critical_node_count": len(critical), "bridge_link_count": len(bridges)}
