# 📡 MeshLab

Simulation-first Meshtastic-style mesh network explorer built with Python and Streamlit. Independent community project, not affiliated with Meshtastic.

## Features

- Deterministic synthetic virtual nodes, adjustable radio range and seed
- Interactive network graph, synthetic signal metrics and shortest-hop route explorer
- Node-outage resilience lab and critical bridge-node identification
- Reproducible simulated event timeline with outage/recovery charts and CSV export
- Single-node reliability comparisons and illustrative range analysis
- Portable JSON simulation report with parameters, network data, and resilience summary
- Scenario planner: save/load portable scenario presets and compare synthetic connectivity side-by-side
- Experimental local USB/TCP Meshtastic radio metadata monitoring, signal history, and CSV export
- Automated unit tests via GitHub Actions

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
# Activate the virtual environment for your platform
python -m pip install -r requirements.txt
streamlit run app.py
```

In the app, choose **Simulation** to explore without hardware. Expand **Simulation settings** to set virtual node count, random seed and illustrative range. Save/load scenario JSON presets, compare alternative layouts, and export JSON reports to reproduce and share a scenario. The report contains synthetic topology data, not live packet data.

Run tests with `python -m pytest -q`.

## Experimental live monitoring

For local radio connections, additionally install `meshtastic` and `pypubsub`. Choose **Live radio (local only)** and connect over USB serial or a private-network TCP address. See [live monitoring documentation](docs/LIVE_MONITORING.md).

**Hardware compatibility has not yet been validated with physical radios.** Streamlit Cloud cannot directly access USB radios connected to your own computer. Do not publicly expose a live radio dashboard.

## Privacy and scientific limitations

Simulation node positions are synthetic. RSSI, SNR and distance are illustrative—not validated LoRa propagation, coverage, or packet-delivery predictions. Graph routes are not Meshtastic firmware routing. The experimental live monitor stores packet metadata in memory without storing payload text, channel keys, or GPS locations.

## Roadmap

1. Verify physical USB and TCP hardware compatibility
2. Improve usability and validate Streamlit deployment
3. Add documented RF models with explicit assumptions
4. Expand event analysis and scenario comparisons

See [v1.0 release notes](docs/RELEASE_NOTES_V1.md).
