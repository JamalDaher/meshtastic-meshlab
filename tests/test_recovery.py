import pytest
from meshlab.recovery import recovery_options, recovery_sequence

DATA = {"nodes": [{"node_id": n} for n in ("a", "b", "c", "d", "e")],
        "links": [{"source": a, "target": b, "snr": 5, "rssi": -80, "distance": 1}
                  for a, b in (("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"))]}

def test_no_failed_nodes():
    assert recovery_options(DATA) == []
    assert recovery_sequence(DATA) == []

def test_bridge_recovery_is_prioritized():
    options = recovery_options(DATA, ["b", "d"])
    assert options[0]["node_id"] in {"b", "d"}
    assert options[0]["largest_group_gain"] > 0

def test_sequence_restores_all_failed_once():
    sequence = recovery_sequence(DATA, ["b", "d"])
    assert sorted(row["node_id"] for row in sequence) == ["b", "d"]
    assert [row["step"] for row in sequence] == [1, 2]

def test_reproducible_order():
    assert recovery_sequence(DATA, ["b", "c", "d"]) == recovery_sequence(DATA, ["d", "c", "b"])

def test_invalid_failed_node():
    with pytest.raises(ValueError):
        recovery_options(DATA, ["missing"])
    with pytest.raises(ValueError):
        recovery_sequence(DATA, ["missing"])
