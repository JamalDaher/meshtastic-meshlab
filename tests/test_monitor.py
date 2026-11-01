from meshlab.monitor import Monitor
from meshlab.gateway import SerialGateway
import pytest

def test_redacts_sensitive_fields():
    monitor = Monitor()
    monitor.ingest({"fromId":"!abc", "rxSnr":4, "rxRssi":-90,
                    "decoded":{"text":"SECRET"}, "position":{"latitude":35},
                    "payload":"SECRET", "channel":7})
    data = str(monitor.snapshot())
    assert "SECRET" not in data
    assert "latitude" not in data
    assert "channel" not in data
    assert "!abc" in data

def test_bounded_events():
    monitor = Monitor(limit=2)
    for i in range(5):
        monitor.ingest({"fromId":f"!{i}"})
    assert len(monitor.snapshot()["events"]) == 2

def test_latest_node_status():
    monitor = Monitor()
    monitor.ingest({"fromId":"!abc", "rxSnr":2})
    monitor.ingest({"fromId":"!abc", "rxSnr":5})
    assert len(monitor.snapshot()["nodes"]) == 1
    assert monitor.snapshot()["nodes"][0]["snr"] == 5

def test_invalid_readings():
    monitor = Monitor()
    monitor.ingest({"fromId":"!abc", "rxSnr":float("nan"), "rxRssi":"-99"})
    assert monitor.snapshot()["events"][0]["snr"] is None
    assert monitor.snapshot()["events"][0]["rssi"] is None

def test_gateway_initially_disconnected():
    gateway = SerialGateway(Monitor())
    assert not gateway.connected
    gateway.disconnect()
    with pytest.raises(ValueError):
        gateway.connect("")
