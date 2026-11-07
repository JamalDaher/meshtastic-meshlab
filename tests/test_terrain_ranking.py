from meshlab.terrain_ranking import rank_terrain_sites

def test_only_evaluated_rf_and_clear_links_count():
    nodes = [{"name": n} for n in "ABC"]
    links = [{"source":"A","target":"B","above_sensitivity":True},
             {"source":"A","target":"C","above_sensitivity":True},
             {"source":"B","target":"C","above_sensitivity":False}]
    rows = [{"source":"A","target":"B","terrain_status":"Clear","fresnel_status":"Clear"},
            {"source":"A","target":"C","terrain_status":"Not evaluated","fresnel_status":"Not evaluated"},
            {"source":"B","target":"C","terrain_status":"Clear","fresnel_status":"Clear"}]
    ranked = rank_terrain_sites(nodes,links,rows)
    by_name = {r["name"]:r for r in ranked}
    assert by_name["A"]["rf_and_terrain_clear"] == 1
    assert by_name["A"]["not_evaluated_links"] == 1
    assert by_name["B"]["rf_and_terrain_clear"] == 1
    assert by_name["C"]["rf_and_terrain_clear"] == 0

def test_blocked_link_not_clear():
    nodes=[{"name":"A"},{"name":"B"}]
    links=[{"source":"A","target":"B","above_sensitivity":True}]
    rows=[{"source":"A","target":"B","terrain_status":"Clear","fresnel_status":"Insufficient"}]
    ranked=rank_terrain_sites(nodes,links,rows)
    assert all(r["rf_and_terrain_clear"]==0 for r in ranked)
