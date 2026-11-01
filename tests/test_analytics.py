from datetime import datetime, timezone, timedelta
from meshlab.analytics import node_activity, signal_series, export_csv

def test_activity_counts_and_staleness():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events = [
        {"node":"a","time":(now-timedelta(minutes=1)).isoformat()},
        {"node":"a","time":(now-timedelta(minutes=2)).isoformat()},
        {"node":"b","time":(now-timedelta(minutes=20)).isoformat()},
    ]
    rows = node_activity(events, now=now)
    assert rows[0]["packets"] == 2 and rows[0]["active"]
    assert not rows[1]["active"]

def test_signal_filter_sorted():
    events = [{"node":"a","time":"2026-01-02","snr":2},
              {"node":"b","time":"2026-01-01","snr":3},
              {"node":"a","time":"2026-01-01","snr":1}]
    assert [r["snr"] for r in signal_series(events, "a")] == [1,2]

def test_export_only_safe_columns():
    data = export_csv([{"node":"=1+1","time":"2026-01-01","snr":2,
                        "rssi":-70,"payload":"PRIVATE","latitude":45}])
    assert "PRIVATE" not in data and "latitude" not in data
    assert "'=1+1" in data
    assert data.splitlines()[0] == "time,node,snr,rssi"
