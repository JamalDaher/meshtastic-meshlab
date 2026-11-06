import pytest
from meshlab.geo import great_circle_km, geographic_links, validate_nodes
from meshlab.rf import RadioProfile

def test_great_circle_known_distance():
    assert great_circle_km(0, 0, 0, 1) == pytest.approx(111.195, abs=0.01)

def test_same_position_zero_distance():
    assert great_circle_km(34, -88, 34, -88) == 0

def test_geographic_link_budget():
    nodes = [{"name": "A", "lat": 34, "lon": -88},
             {"name": "B", "lat": 34.01, "lon": -88}]
    links = geographic_links(nodes, RadioProfile())
    assert len(links) == 1
    assert links[0]["distance_km"] > 1
    assert "link_margin_db" in links[0]

@pytest.mark.parametrize("lat,lon", [(91, 0), (0, -181), (float("nan"), 0)])
def test_reject_bad_coordinates(lat, lon):
    with pytest.raises(ValueError):
        validate_nodes([{"name": "A", "lat": lat, "lon": lon},
                        {"name": "B", "lat": 0, "lon": 0}])

def test_reject_duplicate_names():
    with pytest.raises(ValueError):
        validate_nodes([{"name": "A", "lat": 0, "lon": 0},
                        {"name": "A", "lat": 1, "lon": 1}])
