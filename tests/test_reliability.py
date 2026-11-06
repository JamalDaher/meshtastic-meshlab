import pytest
from meshlab.reliability import single_node_impact, range_comparison

def chain():
    return {"nodes": [{"node_id": n, "name": n} for n in ("a", "b", "c")],
            "links": [{"source": a, "target": b, "snr": 1, "rssi": -70, "distance": 1}
                      for a, b in (("a", "b"), ("b", "c"))]}

def test_chain_center_is_most_critical():
    rows = single_node_impact(chain())
    assert rows[0]["node_id"] == "b"
    assert rows[0]["component_change"] == 1
    assert rows[0]["largest_group_after"] == 1

def test_leaf_removal_keeps_connected():
    rows = {r["node_id"]: r for r in single_node_impact(chain())}
    assert rows["a"]["component_change"] == 0

def test_comparison_reproducible():
    assert range_comparison(8, 42, [2, 4, 6]) == range_comparison(8, 42, [2, 4, 6])

def test_more_range_never_reduces_links():
    rows = range_comparison(8, 42, [2, 4, 6])
    assert [r["links"] for r in rows] == sorted(r["links"] for r in rows)

def test_invalid_range():
    with pytest.raises(ValueError):
        range_comparison(5, 42, [0])
