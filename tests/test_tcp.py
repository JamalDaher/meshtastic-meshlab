import pytest
from meshlab.live import validate_host
from meshlab.gateway import RadioGateway
from meshlab.monitor import Monitor

@pytest.mark.parametrize("host", ["192.168.1.42", "10.0.0.1", "127.0.0.1", "fd00::1"])
def test_local_hosts(host):
    assert validate_host(host)

@pytest.mark.parametrize("host", ["8.8.8.8", "example.com", "", "1.1.1.1"])
def test_reject_nonlocal_hosts(host):
    with pytest.raises(ValueError):
        validate_host(host)

def test_gateway_invalid_transport():
    gateway = RadioGateway(Monitor())
    with pytest.raises(ValueError):
        gateway.connect("192.168.1.5", "invalid")
    assert not gateway.connected
