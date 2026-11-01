"""Thread-safe, bounded, privacy-preserving radio telemetry store."""
from collections import deque
from datetime import datetime, timezone
from threading import Lock

class Monitor:
    def __init__(self, limit=200):
        if limit < 1:
            raise ValueError("limit must be positive")
        self._events = deque(maxlen=limit)
        self._nodes = {}
        self._lock = Lock()

    def ingest(self, packet):
        """Only retain packet metadata; never plaintext, GPS, or payloads."""
        if not isinstance(packet, dict):
            return
        source = packet.get("fromId") or packet.get("from") or "unknown"
        if not isinstance(source, str):
            source = "unknown"
        source = source[:32]
        event = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "node": source, "snr": _number(packet.get("rxSnr")),
                 "rssi": _number(packet.get("rxRssi"))}
        with self._lock:
            self._events.appendleft(event)
            self._nodes[source] = event

    def snapshot(self):
        with self._lock:
            return {"events": list(self._events), "nodes": list(self._nodes.values())}

def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    import math
    return float(value) if math.isfinite(value) else None
