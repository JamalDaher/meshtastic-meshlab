import pytest
from meshlab.simulator import make_nodes, link_metrics, simulate

def test_seed_reproducible():
    assert simulate(8, 42) == simulate(8, 42)

def test_node_ids_unique():
    nodes = make_nodes(30)
    assert len({n.node_id for n in nodes}) == 30

def test_invalid_node_count():
    with pytest.raises(ValueError):
        make_nodes(1)

def test_invalid_range():
    with pytest.raises(ValueError):
        simulate(max_range=0)

def test_link_symmetry():
    a, b = make_nodes(2)
    ab = link_metrics(a, b, 100)
    ba = link_metrics(b, a, 100)
    assert ab["distance"] == ba["distance"]
    assert ab["snr"] == ba["snr"]

def test_links_reference_known_nodes():
    result = simulate(12)
    ids = {n["node_id"] for n in result["nodes"]}
    assert all(l["source"] in ids and l["target"] in ids for l in result["links"])
