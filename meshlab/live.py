"""Optional local Meshtastic readers. Never transmit messages."""
from collections.abc import Callable
import ipaddress

_ALLOWED = tuple(ipaddress.ip_network(cidr) for cidr in
                 ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
                  "127.0.0.0/8", "fc00::/7", "::1/128"))

def validate_host(host: str) -> str:
    """Accept only literal RFC1918, IPv6 ULA or loopback addresses."""
    try:
        address = ipaddress.ip_address(host.strip())
    except (ValueError, AttributeError) as exc:
        raise ValueError("Enter a local IP address, not a hostname") from exc
    if not any(address in network for network in _ALLOWED):
        raise ValueError("Only private LAN or loopback addresses are permitted")
    return str(address)

def _connect(kind: str, target: str, on_packet: Callable[[dict], None]):
    try:
        from pubsub import pub
        if kind == "serial":
            from meshtastic.serial_interface import SerialInterface
            constructor = lambda: SerialInterface(devPath=target)
        elif kind == "tcp":
            from meshtastic.tcp_interface import TCPInterface
            constructor = lambda: TCPInterface(hostname=validate_host(target))
        else:
            raise ValueError("Unsupported connection type")
    except ImportError as exc:
        raise RuntimeError("Install meshtastic and pypubsub for live mode") from exc

    # Meshtastic's pubsub receive topic is process-global; ignore packets
    # from other radio interfaces when the library supplies an interface.
    holder = {"interface": None}
    def receive(packet, interface=None):
        if holder["interface"] is not None and interface is not None and interface is not holder["interface"]:
            return
        if not isinstance(packet, dict):
            return
        on_packet({"from": packet.get("fromId", "unknown"),
                   "rxSnr": packet.get("rxSnr"), "rxRssi": packet.get("rxRssi")})

    pub.subscribe(receive, "meshtastic.receive")
    try:
        connected = constructor()
        holder["interface"] = connected
    except Exception:
        pub.unsubscribe(receive, "meshtastic.receive")
        raise
    return connected, receive

def connect_serial(port: str, on_packet: Callable[[dict], None]):
    return _connect("serial", port, on_packet)

def connect_tcp(host: str, on_packet: Callable[[dict], None]):
    return _connect("tcp", validate_host(host), on_packet)

def disconnect_serial(interface, callback):
    from pubsub import pub
    try:
        pub.unsubscribe(callback, "meshtastic.receive")
    finally:
        interface.close()
