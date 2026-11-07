from datetime import datetime, timezone, timedelta
from meshlab.live_dashboard import live_node_summary

def test_latest_packet_and_stale_status():
    now=datetime(2026,11,7,12,tzinfo=timezone.utc)
    events=[
        {"node":"A","time":(now-timedelta(minutes=7)).isoformat(),"snr":1,"rssi":-110},
        {"node":"A","time":(now-timedelta(seconds=30)).isoformat(),"snr":5,"rssi":-90},
        {"node":"B","time":(now-timedelta(minutes=9)).isoformat(),"snr":2,"rssi":-100}]
    rows=live_node_summary(events,now)
    assert rows[0]["node"]=="A"
    assert rows[0]["last_snr_db"]==5
    assert rows[0]["seconds_since_last_packet"]==30
    assert rows[0]["active_last_5_min"]
    assert not rows[1]["active_last_5_min"]

def test_empty():
    assert live_node_summary([])==[]
