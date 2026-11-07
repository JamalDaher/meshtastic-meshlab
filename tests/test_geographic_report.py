import json
from meshlab.geographic_report import build_geographic_report, report_json

def test_report_marks_missing_terrain_and_is_serializable():
    nodes=[{"name":"A","lat":34,"lon":-88},{"name":"B","lat":34.01,"lon":-88}]
    links=[{"source":"A","target":"B","distance_km":1.1,"link_margin_db":10,
            "above_sensitivity":True}]
    report=build_geographic_report(nodes,links,{},5,5,906.875,0.6,
                                   {"frequency_mhz":906.875})
    assert report["terrain_link_assessments"][0]["terrain_status"]=="Not evaluated"
    assert report["terrain_site_ranking"][0]["rf_and_terrain_clear"]==0
    assert json.loads(report_json(report))["schema_version"]=="meshlab-geographic-report-v1"
