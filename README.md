# 📡 MeshLab

Simulation-first Meshtastic network explorer built with Python and Streamlit.

## v0.1 features
- Reproducible virtual mesh nodes, adjustable count and range
- Synthetic node telemetry and illustrative SNR/RSSI links
- Dashboard with node and link tables
- Automated tests in GitHub Actions
- Optional read-only serial adapter (not yet wired into the UI)

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
Install `meshtastic` and `pypubsub` locally. The `meshlab.live` module provides read-only serial packet metadata. Persistent local gateway controls, TCP, and live UI integration are future milestones.

## Roadmap
1. Network graph with visible links and event timeline
2. Persistent local serial/TCP gateway
3. Live telemetry and privacy controls
4. Coverage analysis and routing experiments

Independent community project; not affiliated with Meshtastic.
