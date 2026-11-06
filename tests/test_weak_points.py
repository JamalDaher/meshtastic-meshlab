from meshlab.weak_points import weak_points

def network(edges, nodes=("a", "b", "c")):
    return {"nodes": [{"node_id": n, "name": n} for n in nodes],
            "links": [{"source": a, "target": b, "snr": 5, "rssi": -80, "distance": 1}
                      for a, b in edges]}

def test_chain_has_bridge_links_and_center():
    result = weak_points(network([("a", "b"), ("b", "c")]))
    assert result["critical_nodes"] == ["b"]
    assert result["bridge_links"] == [("a", "b"), ("b", "c")]

def test_triangle_has_no_weak_points():
    result = weak_points(network([("a", "b"), ("b", "c"), ("c", "a")]))
    assert result["critical_node_count"] == 0
    assert result["bridge_link_count"] == 0

def test_isolated_node_not_critical():
    result = weak_points(network([], nodes=("a", "b")))
    assert result["critical_nodes"] == []
    assert result["bridge_links"] == []

def test_one_link_is_bridge():
    result = weak_points(network([("b", "a")], nodes=("a", "b")))
    assert result["bridge_links"] == [("a", "b")]
