import pytest
from meshlab.terrain import analyze_terrain_profile

def test_flat_short_path_clear():
    result = analyze_terrain_profile([(0, 100), (0.5, 100), (1, 100)], 10, 10)
    assert result["clear_line_of_sight"]
    assert result["minimum_interior_clearance_m"] > 0

def test_hill_blocks_sightline():
    result = analyze_terrain_profile([(0, 100), (0.5, 140), (1, 100)], 5, 5)
    assert not result["clear_line_of_sight"]
    assert result["minimum_interior_clearance_m"] < 0

def test_curvature_blocks_long_low_path():
    result = analyze_terrain_profile([(0, 0), (50, 0), (100, 0)], 2, 2)
    assert not result["clear_line_of_sight"]

def test_reject_unsorted_and_missing_endpoints():
    with pytest.raises(ValueError):
        analyze_terrain_profile([(1, 0), (2, 0)])
    with pytest.raises(ValueError):
        analyze_terrain_profile([(0, 0), (1, 0), (0.5, 0)])

def test_endpoint_antenna_heights():
    result = analyze_terrain_profile([(0, 100), (1, 100)], 3, 8)
    assert result["samples"][0]["clearance_m"] == pytest.approx(3)
    assert result["samples"][-1]["clearance_m"] == pytest.approx(8)
