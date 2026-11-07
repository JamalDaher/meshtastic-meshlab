"""Read-only diagnostics for the local Meshtastic receive session."""
from datetime import datetime, timezone

def connection_diagnostics(connected, events, now=None, stale_after_seconds=300):
    """Connection state is transport state, not proof of RF reachability."""
    if not connected:
        return {"state": "Disconnected", "last_packet_utc": None,
                "seconds_since_packet": None,
                "message": "Connect a local radio to begin receiving packet metadata."}
    now = now or datetime.now(timezone.utc)
    timestamps = []
    for event in events:
        try:
            parsed = datetime.fromisoformat(event["time"])
            if parsed.tzinfo is not None:
                timestamps.append(parsed.astimezone(timezone.utc))
        except (KeyError, ValueError, TypeError, AttributeError):
            continue
    if not timestamps:
        return {"state": "Connected · awaiting packets", "last_packet_utc": None,
                "seconds_since_packet": None,
                "message": "Transport is connected; no packet metadata has been received in this session."}
    latest = max(timestamps)
    age = max(0, int((now - latest).total_seconds()))
    state = "Receiving recently" if age <= stale_after_seconds else "Connected · no recent packets"
    message = ("Received packet metadata within the last five minutes."
               if age <= stale_after_seconds else
               "Transport is connected, but no packets have been observed recently.")
    return {"state": state, "last_packet_utc": latest.isoformat(),
            "seconds_since_packet": age, "message": message}
