from meshlab.topology import build_graph, shortest_route, network_summary
import pytest

def sample():
    return {"nodes": [{"node_id": n} for n in ("a","b","c","d")],
            "links": [{"source":"a","target":"b","snr":5,"rssi":-70,"distance":1},
                      {"source":"b","target":"c","snr":3,"rssi":-80,"distance":2}]}

def test_graph_counts():
    graph = build_graph(sample())
    assert network_summary(graph) == {"nodes":4,"links":2,"components":2}

def test_route():
    assert shortest_route(build_graph(sample()), "a", "c") == ["a","b","c"]

def test_disconnected():
    assert shortest_route(build_graph(sample()), "a", "d") is None

def test_unknown_node():
    with pytest.raises(ValueError):
        shortest_route(build_graph(sample()), "missing", "a")

def test_same_node():
    assert shortest_route(build_graph(sample()), "a", "a") == ["a"]
