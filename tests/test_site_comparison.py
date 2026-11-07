from meshlab.site_comparison import rank_sites

def test_rank_by_reachable_peers():
    nodes = [{"name": name} for name in "ABC"]
    links = [
        {"source": "A", "target": "B", "above_sensitivity": True, "link_margin_db": 8},
        {"source": "A", "target": "C", "above_sensitivity": True, "link_margin_db": 12},
        {"source": "B", "target": "C", "above_sensitivity": False, "link_margin_db": -2},
    ]
    ranked = rank_sites(nodes, links)
    assert ranked[0]["name"] == "A"
    assert ranked[0]["reachable_peers"] == 2
    assert ranked[1]["reachable_peers"] == 1
    assert ranked[0]["weakest_active_margin_db"] == 8

def test_no_active_links():
    rows = rank_sites([{"name": "A"}, {"name": "B"}],
                      [{"source": "A", "target": "B", "above_sensitivity": False, "link_margin_db": -4}])
    assert all(row["reachable_peers"] == 0 for row in rows)
    assert all(row["weakest_active_margin_db"] is None for row in rows)
