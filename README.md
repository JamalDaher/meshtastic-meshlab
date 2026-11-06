# 📡 MeshLab

Simulation-first Meshtastic network explorer built with Python and Streamlit.

## Features
- Reproducible virtual mesh nodes, adjustable count and range
- Synthetic node telemetry and illustrative SNR/RSSI links
- Dashboard with node and link tables
- Automated tests in GitHub Actions
- Interactive synthetic topology and shortest-hop route explorer
- Node-outage what-if lab with critical bridge detection and connected-group analysis
- Optional local USB/TCP radio monitoring with signal history and safe CSV export

**Privacy:** No live messages, channel keys, real locations, or credentials are stored. Simulation coordinates are synthetic. Link metrics are illustrative, not validated RF predictions.

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv
pip install -r requirements.txt
streamlit run app.py
```

## Tests
```bash
python -m pytest -q
```

## Experimental radio adapter
Install `meshtastic` and `pypubsub` locally to connect through the live dashboard. Local USB or private-network TCP connectivity is supported in code but has not been verified with physical hardware. A public hosted app cannot reach your computer USB port. See `docs/LIVE_MONITORING.md`.

## Roadmap
1. Hardware validation for USB and TCP radio monitoring
2. Event timeline and richer diagnostics
3. More realistic RF modeling and coverage experiments
4. Additional network resilience scenarios

Independent community project; not affiliated with Meshtastic.
