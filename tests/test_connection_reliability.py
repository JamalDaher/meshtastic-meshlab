import sys
import types
import pytest
from meshlab.live import validate_host, _connect, disconnect_serial

@pytest.mark.parametrize("address", ["192.168.1.1","10.0.0.2","172.16.0.1","127.0.0.1","fd00::1","::1"])
def test_allowed_lan(address):
    assert validate_host(address)

@pytest.mark.parametrize("address", ["8.8.8.8","example.com","", "100.64.0.1","169.254.1.1","2001:db8::1"])
def test_reject_other_addresses(address):
    with pytest.raises(ValueError):
        validate_host(address)

def test_failed_connection_unsubscribes(monkeypatch):
    calls = []
    class Pub:
        def subscribe(self, fn, topic): calls.append("subscribe")
        def unsubscribe(self, fn, topic): calls.append("unsubscribe")
    pubsub = types.ModuleType("pubsub")
    pubsub.pub = Pub()
    serial = types.ModuleType("meshtastic.serial_interface")
    class Failing:
        def __init__(self, devPath): raise OSError("unavailable")
    serial.SerialInterface = Failing
    package = types.ModuleType("meshtastic")
    package.__path__ = []
    monkeypatch.setitem(sys.modules, "pubsub", pubsub)
    monkeypatch.setitem(sys.modules, "meshtastic", package)
    monkeypatch.setitem(sys.modules, "meshtastic.serial_interface", serial)
    with pytest.raises(OSError):
        _connect("serial", "COM3", lambda packet: None)
    assert calls == ["subscribe", "unsubscribe"]

def test_disconnect_closes_after_unsubscribe_failure(monkeypatch):
    class Pub:
        def unsubscribe(self, fn, topic): raise RuntimeError("unsubscribe")
    module = types.ModuleType("pubsub")
    module.pub = Pub()
    monkeypatch.setitem(sys.modules, "pubsub", module)
    class Interface:
        closed = False
        def close(self): self.closed = True
    interface = Interface()
    with pytest.raises(RuntimeError):
        disconnect_serial(interface, lambda _: None)
    assert interface.closed
