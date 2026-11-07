from datetime import datetime, timezone, timedelta
from meshlab.connection_diagnostics import connection_diagnostics

def test_disconnected_overrides_packets():
    assert connection_diagnostics(False, [{"time":"2026-11-07T12:00:00+00:00"}])["state"]=="Disconnected"

def test_connected_awaiting_packets():
    assert connection_diagnostics(True, [])["state"]=="Connected · awaiting packets"

def test_recent_and_stale():
    now=datetime(2026,11,7,12,tzinfo=timezone.utc)
    recent={"time":(now-timedelta(seconds=30)).isoformat()}
    stale={"time":(now-timedelta(minutes=8)).isoformat()}
    assert connection_diagnostics(True,[stale,recent],now)["state"]=="Receiving recently"
    assert connection_diagnostics(True,[stale],now)["state"]=="Connected · no recent packets"

def test_bad_timestamps_do_not_crash():
    assert connection_diagnostics(True,[{"time":"invalid"},{}])["last_packet_utc"] is None
