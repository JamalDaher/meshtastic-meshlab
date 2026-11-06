import json
import pytest
from meshlab.scenarios import encode_scenario, decode_scenario, compare_scenarios, validate_scenario

BASE = {"count": 8, "seed": 42, "radius": 5.0}

def test_round_trip():
    assert decode_scenario(encode_scenario(BASE)) == BASE

def test_comparison_identical_scenarios():
    assert all(row["difference_b_minus_a"] == 0 for row in compare_scenarios(BASE, BASE))

def test_comparison_is_reproducible():
    other = {**BASE, "radius": 7.0}
    assert compare_scenarios(BASE, other) == compare_scenarios(BASE, other)

@pytest.mark.parametrize("bad", [
    {"count": True, "seed": 42, "radius": 5},
    {"count": 8, "seed": 42, "radius": float("nan")},
    {"count": 8, "seed": 42, "radius": -1},
    {"count": 8, "seed": 42, "radius": 5, "extra": 1},
])
def test_reject_invalid_settings(bad):
    with pytest.raises(ValueError):
        validate_scenario(bad)

def test_reject_unsupported_format():
    with pytest.raises(ValueError):
        decode_scenario(json.dumps({"format": "unknown", "settings": BASE}))

def test_reject_large_file():
    with pytest.raises(ValueError):
        decode_scenario(" " * 8193)
