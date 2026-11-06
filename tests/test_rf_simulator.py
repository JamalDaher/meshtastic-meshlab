import pytest
from meshlab.rf import RadioProfile
from meshlab.rf_simulator import simulate_rf

def test_reproducible_rf_network():
    assert simulate_rf(8, 42) == simulate_rf(8, 42)

def test_sensitivity_changes_links():
    strong = simulate_rf(10, 42, 0.5, RadioProfile(receiver_sensitivity_dbm=-150))
    weak = simulate_rf(10, 42, 0.5, RadioProfile(receiver_sensitivity_dbm=-50))
    assert len(strong["links"]) > len(weak["links"])

def test_link_fields_work_with_topology():
    from meshlab.topology import build_graph
    network = simulate_rf(8, 42)
    graph = build_graph(network)
    assert graph.number_of_nodes() == 8
    assert all("link_margin_db" in link for link in network["links"])

@pytest.mark.parametrize("scale", [0, -1, float("nan"), float("inf")])
def test_invalid_scale(scale):
    with pytest.raises(ValueError):
        simulate_rf(km_per_unit=scale)
