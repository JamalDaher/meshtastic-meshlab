import pytest
from meshlab.terrain import analyze_terrain_profile
from meshlab.fresnel import analyze_fresnel_clearance

def test_fresnel_radius_midpoint():
    terrain = analyze_terrain_profile([(0, 100), (0.5, 100), (1, 100)], 5, 5)
    result = analyze_fresnel_clearance(terrain, frequency_mhz=900, clearance_fraction=0.6)
    assert result["samples"][1]["fresnel_radius_m"] == pytest.approx(9.125, abs=0.03)
    assert result["samples"][0]["fresnel_radius_m"] == 0

def test_geometric_clear_can_fail_fresnel():
    terrain = analyze_terrain_profile([(0, 100), (0.5, 100), (1, 100)], 2, 2)
    assert terrain["clear_line_of_sight"]
    assert not analyze_fresnel_clearance(terrain)["fresnel_clear"]

def test_high_antennas_clear():
    terrain = analyze_terrain_profile([(0, 100), (0.5, 100), (1, 100)], 30, 30)
    assert analyze_fresnel_clearance(terrain)["fresnel_clear"]

@pytest.mark.parametrize("freq,fraction", [(0, 0.6), (900, 1.1), (float("nan"), 0.6)])
def test_bad_inputs(freq, fraction):
    terrain = analyze_terrain_profile([(0, 0), (1, 0)])
    with pytest.raises(ValueError):
        analyze_fresnel_clearance(terrain, freq, fraction)
