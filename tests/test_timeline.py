import pytest
from meshlab.simulator import simulate
from meshlab.timeline import generate_timeline

def test_deterministic():
    data = simulate(8, 12)
    assert generate_timeline(data, 99) == generate_timeline(data, 99)

def test_bounds():
    data = simulate(4)
    with pytest.raises(ValueError):
        generate_timeline(data, steps=0)
    with pytest.raises(ValueError):
        generate_timeline(data, steps=201)

def test_events_have_consistent_node_counts():
    data = simulate(6)
    events = generate_timeline(data, steps=30)
    assert len(events) == 30
    assert all(e["active_nodes"] + e["offline_count"] == 6 for e in events)
    assert all(0 <= e["largest_group"] <= e["active_nodes"] for e in events)

def test_node_toggle_sequence():
    data = simulate(2)
    events = generate_timeline(data, steps=10)
    offline = set()
    for event in events:
        node = event["node"]
        if event["event"] == "offline":
            assert node not in offline
            offline.add(node)
        else:
            assert node in offline
            offline.remove(node)
        assert len(offline) == event["offline_count"]
