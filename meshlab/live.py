"""Optional local Meshtastic readers. Never transmit messages."""
from collections.abc import Callable
import ipaddress

def validate_host(host: str) -> str:
    """Allow only literal private or loopback IPv4/IPv6 addresses."""
    try:
        address = ipaddress.ip_address(host.strip())
    except (ValueError, AttributeError) as exc:
        raise ValueError("Enter a private or loopback IP address, not a hostname") from exc
    if not (address.is_private or address.is_loopback):
        raise ValueError("Public addresses are not permitted")
    return str(address)

def _connect(kind: str, target: str, on_packet: Callable[[dict], None]):
    try:
        from pubsub import pub
        if kind == "serial":
            from meshtastic.serial_interface import SerialInterface
            constructor = lambda: SerialInterface(devPath=target)
        else:
            from meshtastic.tcp_interface import TCPInterface
            constructor = lambda: TCPInterface(hostname=validate_host(target))
    except ImportError as exc:
        raise RuntimeError("Install meshtastic and pypubsub for live mode") from exc

    def receive(packet, interface=None):
        on_packet({"from": packet.get("fromId", "unknown"),
                   "rxSnr": packet.get("rxSnr"), "rxRssi": packet.get("rxRssi")})

    pub.subscribe(receive, "meshtastic.receive")
    try:
        interface = constructor()
    except Exception:
        pub.unsubscribe(receive, "meshtastic.receive")
        raise
    return interface, receive

def connect_serial(port: str, on_packet: Callable[[dict], None]):
    return _connect("serial", port, on_packet)

def connect_tcp(host: str, on_packet: Callable[[dict], None]):
    return _connect("tcp", validate_host(host), on_packet)

def disconnect_serial(interface, callback):
    from pubsub import pub
    pub.unsubscribe(callback, "meshtastic.receive")
    interface.close()
