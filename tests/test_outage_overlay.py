import pytest
from meshlab.outage_overlay import outage_overlay

DATA = {"nodes": [{"node_id": n} for n in ("a", "b", "c")],
        "links": [{"source": a, "target": b, "snr": 5, "rssi": -80, "distance": 1}
                  for a, b in (("a", "b"), ("b", "c"))]}

def test_offline_node_removes_incident_links():
    result = outage_overlay(DATA, ["b"])
    assert result["offline_nodes"] == ["b"]
    assert result["online_nodes"] == ["a", "c"]
    assert result["active_links"] == []
    assert result["state"]["components"] == 2

def test_no_outage_keeps_all_links():
    result = outage_overlay(DATA)
    assert len(result["active_links"]) == 2
    assert result["state"]["components"] == 1

def test_all_offline():
    result = outage_overlay(DATA, ["a", "b", "c"])
    assert result["online_nodes"] == []
    assert result["state"]["components"] == 0

def test_unknown_node_rejected():
    with pytest.raises(ValueError):
        outage_overlay(DATA, ["missing"])
