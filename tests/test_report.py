import json
from meshlab.report import build_report, export_json

def test_report_deterministic():
    assert export_json(build_report(8, 42, 5.0)) == export_json(build_report(8, 42, 5.0))

def test_report_summary_matches_network():
    report = build_report(6, 10, 4.0)
    assert report["summary"]["nodes"] == len(report["network"]["nodes"])
    assert report["summary"]["links"] == len(report["network"]["links"])
    assert len(report["node_impact"]) == 6

def test_report_json_round_trip():
    report = build_report(4, 1, 3.0)
    assert json.loads(export_json(report)) == report
    assert report["kind"] == "synthetic-meshlab-report"
