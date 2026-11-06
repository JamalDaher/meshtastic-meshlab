"""Portable simulation scenarios and fair side-by-side comparisons."""
import json
import math
from meshlab.report import build_report

def validate_scenario(value):
    if not isinstance(value, dict) or set(value) != {"count", "seed", "radius"}:
        raise ValueError("Scenario requires count, seed and radius")
    count, seed, radius = value["count"], value["seed"], value["radius"]
    if type(count) is not int or not 2 <= count <= 50:
        raise ValueError("count must be an integer from 2 to 50")
    if type(seed) is not int or not 0 <= seed <= 100000:
        raise ValueError("seed must be an integer from 0 to 100000")
    if type(radius) not in (int, float) or not math.isfinite(radius) or not 0 < radius <= 100:
        raise ValueError("radius must be a finite positive number at most 100")
    return {"count": count, "seed": seed, "radius": float(radius)}

def encode_scenario(value):
    return json.dumps({"format": "meshlab-scenario-v1", "settings": validate_scenario(value)},
                      indent=2, sort_keys=True) + "\n"

def decode_scenario(raw):
    if len(raw) > 8192:
        raise ValueError("Scenario file is too large")
    value = json.loads(raw)
    if not isinstance(value, dict) or value.get("format") != "meshlab-scenario-v1":
        raise ValueError("Unsupported scenario format")
    return validate_scenario(value.get("settings"))

def compare_scenarios(left, right):
    left, right = validate_scenario(left), validate_scenario(right)
    a = build_report(left["count"], left["seed"], left["radius"])["summary"]
    b = build_report(right["count"], right["seed"], right["radius"])["summary"]
    metrics = ("nodes", "links", "connected_groups", "largest_group")
    return [{"metric": metric, "scenario_a": a[metric], "scenario_b": b[metric],
             "difference_b_minus_a": b[metric] - a[metric]} for metric in metrics]
