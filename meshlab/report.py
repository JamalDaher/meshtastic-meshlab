"""Portable, deterministic synthetic simulation report exports."""
import json
from meshlab.simulator import simulate
from meshlab.resilience import analyze_failure, critical_nodes
from meshlab.reliability import single_node_impact

def build_report(count: int, seed: int, radius: float) -> dict:
    data = simulate(count, seed, radius)
    baseline = analyze_failure(data)
    return {
        "schema_version": 1,
        "kind": "synthetic-meshlab-report",
        "parameters": {"nodes": count, "seed": seed, "range": radius},
        "summary": {
            "nodes": baseline["remaining_nodes"],
            "links": baseline["remaining_links"],
            "connected_groups": baseline["components"],
            "largest_group": baseline["largest_component"],
            "critical_nodes": critical_nodes(data),
        },
        "node_impact": single_node_impact(data),
        "network": data,
        "disclaimer": "Synthetic graph analysis only; not real radio telemetry or a validated RF prediction.",
    }

def export_json(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
