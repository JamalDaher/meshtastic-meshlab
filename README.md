# 📡 MeshLab

**[Launch MeshLab — Live Streamlit App](https://meshlab.streamlit.app/)**

Simulation-first Meshtastic-style mesh network explorer built with Python and Streamlit. Independent community project, not affiliated with Meshtastic.

## Workspace navigation

The simulation dashboard groups tools into five tabs: **Network** (topology and routes), **Resilience** (outages and recovery), **Analysis** (timeline and reliability), **Scenarios** (save, compare and export), and **Geographic** (maps, RF links, terrain and Fresnel analysis). Select a tab to focus on one task without scrolling through the entire dashboard.

## v1.1 release

The v1.1 network-planning milestone adds a compact, outage-aware simulation summary, shared offline-node controls across tabs, optional node labels, and route highlighting. See [v1.1 release notes and validation checklist](docs/RELEASE_NOTES_V1_1.md). The simulation is illustrative rather than an RF prediction.

## v1.2 Advanced RF Planning

The Network tab includes an independent **ideal free-space RF link budget explorer** with configurable frequency, transmit power, antenna gains, cable losses, receiver sensitivity and link distance. It reports free-space path loss, estimated received power and margin. The independent explorer does not change topology; the separate selectable RF connectivity mode does. Neither is terrain-aware or a validated LoRa coverage prediction.

## RF connectivity mode

Simulation settings can switch between the original distance threshold and an **ideal free-space RF threshold**. The RF mode uses an explicit kilometers-per-synthetic-unit scale and configurable frequency, TX power, antenna gains, cable loss and receiver sensitivity. Link tables include estimated path loss, received power and link margin. This is an idealized estimate, not calibrated coverage. Timeline and range comparisons still use the original distance model. Dedicated RF scenario and report exports preserve RF settings separately from legacy exports.

## RF margin visualization

In ideal free-space RF mode, the Network topology can color active links by estimated link margin: red (0–6 dB), amber (6–15 dB), and teal (15 dB and above). Hover to see the modeled margin. Links below receiver sensitivity are not drawn. These thresholds are illustrative, not calibrated reliability predictions. Disable margin coloring to show orange graph bridge links instead.

## RF presets and reports

In ideal RF connectivity mode, the Scenarios tab can download a versioned RF settings preset and a reproducible RF simulation report containing the selected radio profile, coordinate scale, computed network links, link margins and graph summary. Uploaded RF presets can be validated and inspected, and applied to the current simulation with **Apply RF scenario to simulation** (up to the dashboard limit of 30 nodes). Legacy distance-model presets and reports remain separate for backward compatibility.

See [v1.2 release notes and validation checklist](docs/RELEASE_NOTES_V1_2.md) before publishing the v1.2.0 release.

## v1.3 geographic planning preview

The dedicated Geographic tab keeps advanced radio controls and link tables collapsible for easier mobile use. It includes a site comparison table ranked by idealized reachable peers and weakest active margin (with CSV export), plus a geographic planning section with editable node names and latitude/longitude, a node-position map, great-circle distances, ideal free-space RF link budgets, and CSV export. Coordinates are supplied manually; no device location is collected. The interactive map shows node positions, margin-colored estimated links, and optional user-defined planning radius rings (0.5–100 km), alongside the separately displayed ideal free-space sensitivity radius and adjustable reserve margin. These are **not** terrain-aware or guaranteed coverage predictions. Terrain, obstructions, fading and interference are not modeled. The existing synthetic topology remains unchanged.

## Terrain line-of-sight preview (v1.3)

A manual elevation-profile tool in Geographic accepts ordered distance/elevation samples, antenna heights and reports geometric terrain clearance with an approximate effective Earth-radius correction. It can optionally fetch elevation samples from the public Open-Meteo elevation API when the user explicitly clicks Fetch; selected geographic coordinates are sent to that service, account for vegetation/buildings. Fetched elevation profiles are associated with the selected geographic node pair; switching endpoints requires a new fetch before interpreting that link. Site rankings remain ideal free-space only. The panel also estimates first Fresnel-zone clearance at sampled points with adjustable frequency and required clearance percentage; this is not a diffraction or propagation model. Results are only as reliable as the supplied samples.

## Features

- Deterministic synthetic virtual nodes, adjustable radio range and seed
- Interactive network graph, synthetic signal metrics and shortest-hop route explorer
- Node-outage resilience lab and critical bridge-node identification
- Optional orange highlights for critical nodes and bridge links on the topology graph
- Interactive node-outage overlays: grey offline nodes and remove their links from the active diagram
- Greedy recovery planner ranks offline nodes by connectivity restored and exports recovery sequences
- Reproducible simulated event timeline with outage/recovery charts and CSV export
- Single-node reliability comparisons and illustrative range analysis
- Portable JSON simulation report with parameters, network data, and resilience summary
- Scenario planner: save/load portable scenario presets and compare synthetic connectivity side-by-side
- Experimental local USB/TCP Meshtastic radio metadata monitoring, signal history, and CSV export
- Automated unit tests via GitHub Actions

## Hosted Streamlit deployment

MeshLab is deployed at **https://meshlab.streamlit.app/** and can run as a simulation-first app on Streamlit Community Cloud. See [deployment instructions](docs/STREAMLIT_DEPLOYMENT.md). For hosted demos, set `MESHLAB_SIMULATION_ONLY=1` to hide local radio connection controls. The hosted URL is assigned by Streamlit after deployment.

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

For multi-link planning, explicitly fetch and save each link's elevation profile, then open **Compare saved link terrain profiles** to review sampled geometric and Fresnel status or export CSV. Saved profiles are session-only, bound to exact site coordinates, and unassessed links remain marked **Not evaluated**. This does not automatically fetch terrain for every link or validate real RF reliability.

The Geographic workspace also ranks sites by **evaluated** RF-above-sensitivity links with sampled terrain and Fresnel clearance. It shows how many links are unevaluated and never treats missing terrain as clear. The ranking is limited to sampled elevations, assumes shared antenna heights and does not model vegetation, diffraction, or measured packet reliability.

The terrain panel includes a discrete **Antenna-height planner** that raises both endpoint antennas by equal increments to find the first sampled Fresnel-clear configuration within a user-selected limit. It does not optimize independently, model clutter, or certify tower heights.
