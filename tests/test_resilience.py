import pytest
from meshlab.resilience import analyze_failure, critical_nodes

def example():
    return {"nodes": [{"node_id": n} for n in ("a", "b", "c", "d")],
            "links": [{"source": "a", "target": "b"},
                      {"source": "b", "target": "c"},
                      {"source": "c", "target": "d"}]}

def test_bridge_node_disconnects():
    assert critical_nodes(example()) == ["b", "c"]
    result = analyze_failure(example(), ["b"])
    assert result["components"] == 2
    assert result["remaining_nodes"] == 3
    assert result["largest_component"] == 2

def test_no_failure():
    result = analyze_failure(example())
    assert result["components"] == result["baseline_components"] == 1

def test_all_nodes_removed():
    result = analyze_failure(example(), ["a", "b", "c", "d"])
    assert result["components"] == 0
    assert result["largest_component"] == 0

def test_unknown_node_rejected():
    with pytest.raises(ValueError):
        analyze_failure(example(), ["missing"])

def test_no_critical_nodes_in_triangle():
    data = example()
    data["links"].append({"source": "a", "target": "c"})
    data["links"].append({"source": "a", "target": "d"})
    assert critical_nodes(data) == []
