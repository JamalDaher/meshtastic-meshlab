# Local live monitoring

MeshLab's local serial gateway is opt-in and read-only. It never sends messages or changes radio settings.

## Install

```bash
pip install -r requirements.txt
pip install meshtastic pypubsub
```

## Connection

Attach your radio to the computer running MeshLab, identify its serial port, and use the **Live radio (local only)** workspace tab. Connection is explicit; disconnect before unplugging. A hosted Streamlit app cannot access your computer's USB devices.

Only packet sender ID, RSSI, SNR and reception timestamp are retained in memory. Message text, payloads, channel keys, and GPS coordinates are excluded. No telemetry is uploaded by MeshLab.

## Limitations

The gateway currently supports serial only. The network table shows nodes observed through received packets, not necessarily every node in the radio's node database. Radio hardware and firmware vary; check compatibility with the official Meshtastic Python package. Local TCP support and node database discovery are planned.
