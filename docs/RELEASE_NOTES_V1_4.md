# MeshLab v1.4.0 — Live Network Diagnostics

## Highlights

MeshLab v1.4 expands its existing **local-only** Meshtastic receive mode with a read-only diagnostics dashboard. The hosted Streamlit demo remains simulation-first and must be configured simulation-only using `MESHLAB_SIMULATION_ONLY=1`.

- **Live node status:** last observed packet, activity in the last five minutes, latest RSSI/SNR, and observed packet counts.
- **Connection diagnostics:** disconnected, connected but awaiting packets, recently receiving, and connected without recent packets.
- **Observed signal statistics:** per-node RSSI/SNR mean, minimum, maximum, and valid sample counts.
- **Signal history comparisons:** compare selected nodes on separate RSSI (dBm) or SNR (dB) plots.
- **Receive-data diagnostics:** flag stale observations, fewer than three observed packets, and missing RSSI/SNR readings.

## Privacy and limitations

- Live monitoring is **read-only**. No commands or packets are transmitted by these dashboards.
- Retained metadata is bounded and in memory: observed sender ID, reception timestamp, RSSI and SNR. No message text, payloads or GPS positions are retained.
- Node status and diagnostics reflect **received packet metadata**, not proof of device reachability, two-way connectivity, delivery rate, or hardware failure.
- Sampled packet counts depend on what the connected receiver heard; absence of packets does not establish a failed node.
- Plot lines connect discrete observations, not continuous RF measurements.
- USB serial and private-LAN TCP require a **local installation** with optional `meshtastic` and `pypubsub` packages. Browser-based Streamlit Cloud cannot directly access a user's local USB radio.

## Release validation checklist

- [ ] All GitHub Actions checks pass on the release-prep PR and main.
- [ ] Simulation, Geographic, Scenarios, and other existing tabs still work.
- [ ] Run locally with optional radio dependencies and a compatible Meshtastic device.
- [ ] Confirm USB serial connection, packet reception, disconnect, and reconnect.
- [ ] Confirm private-LAN TCP connection and that public IP addresses are rejected.
- [ ] Verify connection states before first packet, after recent packets, and after five minutes without traffic.
- [ ] Verify node status, RSSI/SNR statistics, comparison charts, and diagnostic flags with real received packets.
- [ ] Confirm no message contents or position information are shown or exported.
- [ ] Confirm hosted deployment is configured to disable live-radio mode.
- [ ] Create GitHub release with tag `v1.4.0` and title **MeshLab v1.4.0 — Live Network Diagnostics**.

## Included pull requests

- #44 Read-only live node dashboard
- #45 Local connection and receive diagnostics
- #46 Per-node RSSI/SNR statistics
- #47 Multi-node signal history comparisons
- #48 Receive-data diagnostics

Independent community project; not affiliated with Meshtastic.
