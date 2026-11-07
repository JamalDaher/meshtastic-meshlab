from meshlab.site_terrain import link_key, summarize_saved_links

def test_symmetric_key_and_coordinate_invalidation():
    a = {"name": "A", "lat": 34, "lon": -88}
    b = {"name": "B", "lat": 35, "lon": -88}
    assert link_key(a, b) == link_key(b, a)
    assert link_key(a, b) != link_key(a, {**b, "lat": 35.1})

def test_saved_and_missing_links():
    nodes = [{"name": "A", "lat": 34, "lon": -88},
             {"name": "B", "lat": 34.01, "lon": -88},
             {"name": "C", "lat": 34.02, "lon": -88}]
    links = [{"source": "A", "target": "B", "distance_km": 1, "link_margin_db": 20},
             {"source": "B", "target": "C", "distance_km": 1, "link_margin_db": 18}]
    saved = {link_key(nodes[0], nodes[1]): [(0, 100), (0.5, 100), (1, 100)]}
    rows = summarize_saved_links(nodes, links, saved, 30, 30, 906.875, 0.6)
    assert rows[0]["terrain_status"] == "Clear"
    assert rows[0]["fresnel_status"] == "Clear"
    assert rows[1]["terrain_status"] == "Not evaluated"
