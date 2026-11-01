"""Optional local Meshtastic reader. Never transmits messages."""
from collections.abc import Callable

def connect_serial(port: str, on_packet: Callable[[dict], None]):
    """Connect to a locally attached radio; caller must close the interface.

    Install the optional meshtastic package first. This is intentionally not
    used in hosted demos; serial ports require local hardware access.
    """
    try:
        import meshtastic.serial_interface
        from pubsub import pub
    except ImportError as exc:
        raise RuntimeError("Install meshtastic and pypubsub for live mode") from exc

    def receive(packet, interface=None):
        # Only expose minimal metadata by default; never store message text.
        on_packet({"from": packet.get("fromId", "unknown"),
                   "rxSnr": packet.get("rxSnr"),
                   "rxRssi": packet.get("rxRssi")})

    pub.subscribe(receive, "meshtastic.receive")
    try:
        interface = meshtastic.serial_interface.SerialInterface(devPath=port)
    except Exception:
        pub.unsubscribe(receive, "meshtastic.receive")
        raise
    return interface, receive

def disconnect_serial(interface, callback):
    from pubsub import pub
    pub.unsubscribe(callback, "meshtastic.receive")
    interface.close()
