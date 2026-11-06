import math
import pytest
from meshlab.coverage import theoretical_radius_km, coverage_ring
from meshlab.geo import great_circle_km
from meshlab.rf import RadioProfile, link_budget

def test_radius_matches_link_budget_threshold():
    p = RadioProfile()
    radius = theoretical_radius_km(p)
    assert abs(link_budget(radius, p)["link_margin_db"]) <= 0.02

def test_reserve_margin_reduces_radius():
    assert theoretical_radius_km(reserve_margin_db=12) < theoretical_radius_km()

def test_circle_geographic_distance():
    ring = coverage_ring(34.25, -88.4, 10)
    assert len(ring) == 73
    assert ring[0] == pytest.approx(ring[-1])
    for lat, lon in ring[::9]:
        assert great_circle_km(34.25, -88.4, lat, lon) == pytest.approx(10, abs=0.02)

@pytest.mark.parametrize("radius", [0, -1, float("inf")])
def test_invalid_radius(radius):
    with pytest.raises(ValueError):
        coverage_ring(0, 0, radius)
