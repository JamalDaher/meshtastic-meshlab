from datetime import datetime, timezone, timedelta
from meshlab.network_diagnostics import diagnostic_rows, diagnostic_totals

def test_flags_sparse_stale_and_missing_signals():
    now=datetime(2026,11,7,12,tzinfo=timezone.utc)
    events=[
        {"node":"A","time":(now-timedelta(minutes=10)).isoformat(),"snr":None,"rssi":None},
        {"node":"B","time":(now-timedelta(seconds=20)).isoformat(),"snr":5,"rssi":-95},
        {"node":"B","time":(now-timedelta(seconds=30)).isoformat(),"snr":6,"rssi":-94},
        {"node":"B","time":(now-timedelta(seconds=40)).isoformat(),"snr":7,"rssi":-93}]
    rows=diagnostic_rows(events,now)
    assert rows[0]["node"]=="A"
    assert rows[0]["flags_count"]==4
    assert rows[1]["flags_count"]==0
    assert diagnostic_totals(rows)["nodes_with_flags"]==1

def test_empty():
    assert diagnostic_rows([])==[]
    assert diagnostic_totals([])["observed_nodes"]==0
