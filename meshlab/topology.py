"""Pure graph analysis for simulated mesh networks."""
import networkx as nx

def build_graph(data: dict) -> nx.Graph:
    graph = nx.Graph()
    for node in data["nodes"]:
        graph.add_node(node["node_id"])
    for link in data["links"]:
        graph.add_edge(link["source"], link["target"], snr=link["snr"],
                       rssi=link["rssi"], distance=link["distance"])
    return graph

def shortest_route(graph: nx.Graph, source: str, target: str) -> list[str] | None:
    if source not in graph or target not in graph:
        raise ValueError("Unknown source or target node")
    try:
        return nx.shortest_path(graph, source, target)
    except nx.NetworkXNoPath:
        return None

def network_summary(graph: nx.Graph) -> dict:
    return {"nodes": graph.number_of_nodes(), "links": graph.number_of_edges(),
            "components": nx.number_connected_components(graph)}
