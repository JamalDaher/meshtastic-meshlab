"""Versioned, reproducible RF scenario presets and simulation reports."""
import json
import math
from dataclasses import asdict
from meshlab.rf import RadioProfile
from meshlab.rf_simulator import simulate_rf
from meshlab.resilience import analyze_failure, critical_nodes
from meshlab.reliability import single_node_impact

RF_FORMAT = "meshlab-rf-scenario-v1"

def validate_rf_settings(settings):
    if not isinstance(settings, dict) or set(settings) != {"count", "seed", "km_per_unit", "profile"}:
        raise ValueError("RF settings must include count, seed, km_per_unit and profile")
    count, seed, scale = settings["count"], settings["seed"], settings["km_per_unit"]
    if type(count) is not int or not 2 <= count <= 50:
        raise ValueError("count must be an integer between 2 and 50")
    if type(seed) is not int or not 0 <= seed <= 100000:
        raise ValueError("seed must be an integer between 0 and 100000")
    if type(scale) not in (int, float) or not math.isfinite(scale) or not 0 < scale <= 100:
        raise ValueError("km_per_unit must be finite, positive and at most 100")
    raw = settings["profile"]
    fields = set(RadioProfile.__dataclass_fields__)
    if not isinstance(raw, dict) or set(raw) != fields:
        raise ValueError("RF profile fields are missing or unexpected")
    if any(type(v) not in (int, float) for v in raw.values()):
        raise ValueError("RF profile values must be numbers")
    profile = RadioProfile(**raw)
    return {"count": count, "seed": seed, "km_per_unit": float(scale), "profile": asdict(profile)}

def encode_rf_scenario(settings):
    return json.dumps({"format": RF_FORMAT, "settings": validate_rf_settings(settings)},
                      indent=2, sort_keys=True, allow_nan=False) + "\n"

def decode_rf_scenario(raw):
    if len(raw) > 16384:
        raise ValueError("RF scenario exceeds size limit")
    obj = json.loads(raw)
    if not isinstance(obj, dict) or obj.get("format") != RF_FORMAT:
        raise ValueError("Unsupported RF scenario format")
    return validate_rf_settings(obj.get("settings"))

def build_rf_report(settings):
    settings = validate_rf_settings(settings)
    network = simulate_rf(settings["count"], settings["seed"], settings["km_per_unit"],
                          RadioProfile(**settings["profile"]))
    baseline = analyze_failure(network)
    return {
        "schema_version": 2, "kind": "synthetic-meshlab-rf-report",
        "model": "ideal-free-space-threshold", "settings": settings,
        "summary": {"nodes": baseline["remaining_nodes"],
                    "links": baseline["remaining_links"],
                    "connected_groups": baseline["components"],
                    "largest_group": baseline["largest_component"],
                    "critical_nodes": critical_nodes(network)},
        "node_impact": single_node_impact(network),
        "network": network,
        "disclaimer": "Ideal free-space estimate on synthetic coordinates; not measured RF, terrain-aware coverage, or Meshtastic packet delivery."
    }
