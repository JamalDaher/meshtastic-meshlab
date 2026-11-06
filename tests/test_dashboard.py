from meshlab.dashboard import simulation_dashboard

DATA = {"nodes": [{"node_id": n} for n in ("a", "b", "c")],
        "links": [{"source": a, "target": b, "snr": 5, "rssi": -80, "distance": 1}
                  for a, b in (("a", "b"), ("b", "c"))]}

def test_baseline_dashboard():
    d = simulation_dashboard(DATA)
    assert (d["online_nodes"], d["active_links"], d["connected_groups"]) == (3, 2, 1)
    assert d["largest_group_pct"] == 100.0
    assert (d["critical_nodes"], d["bridge_links"]) == (1, 2)

def test_outage_dashboard():
    d = simulation_dashboard(DATA, ["b"])
    assert (d["online_nodes"], d["offline_nodes"], d["active_links"]) == (2, 1, 0)
    assert d["connected_groups"] == 2
    assert d["largest_group_pct"] == 50.0

def test_all_offline_safe_percentage():
    d = simulation_dashboard(DATA, ["a", "b", "c"])
    assert d["online_nodes"] == 0
    assert d["largest_group_pct"] == 0.0

def test_empty_graph_safe_percentage():
    d = simulation_dashboard({"nodes": [], "links": []})
    assert d["total_nodes"] == 0
    assert d["largest_group_pct"] == 0.0
