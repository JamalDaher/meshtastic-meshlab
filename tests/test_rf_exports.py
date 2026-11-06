import json
import pytest
from dataclasses import asdict
from meshlab.rf import RadioProfile
from meshlab.rf_exports import validate_rf_settings, encode_rf_scenario, decode_rf_scenario, build_rf_report

SETTINGS = {"count": 8, "seed": 42, "km_per_unit": 0.5, "profile": asdict(RadioProfile())}

def test_rf_scenario_roundtrip():
    assert decode_rf_scenario(encode_rf_scenario(SETTINGS)) == SETTINGS

def test_rf_report_reproducible():
    a, b = build_rf_report(SETTINGS), build_rf_report(SETTINGS)
    assert a == b
    assert a["kind"] == "synthetic-meshlab-rf-report"
    assert a["summary"]["links"] == len(a["network"]["links"])

def test_reject_legacy_scenario():
    with pytest.raises(ValueError):
        decode_rf_scenario(json.dumps({"format": "meshlab-scenario-v1", "settings": SETTINGS}))

def test_reject_invalid_profile():
    broken = {**SETTINGS, "profile": {**SETTINGS["profile"], "frequency_mhz": 0}}
    with pytest.raises(ValueError):
        validate_rf_settings(broken)

def test_reject_nonfinite_profile():
    broken = {**SETTINGS, "profile": {**SETTINGS["profile"], "frequency_mhz": float("nan")}}
    with pytest.raises(ValueError):
        encode_rf_scenario(broken)
