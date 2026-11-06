# MeshLab v1.1.0 — Network Planning and Streamlit

Release candidate documentation. Publish the GitHub release **only after CI and hosted smoke tests pass**.

## Highlights
- Portable saved scenario presets and side-by-side connectivity comparisons
- Critical-node and bridge-link visualization
- Interactive offline-node overlays and outage-aware route exploration
- Greedy node restoration planning and CSV export
- Streamlit Community Cloud deployment guide and hosted app link
- Four workspace tabs: Network, Resilience, Analysis, Scenarios
- Shared offline-node controls, a compact outage-aware summary, optional labels, and a highlighted route detail view

## Compatibility
- Existing synthetic report and scenario JSON formats remain unchanged.
- The hosted app is for simulation. Experimental USB/TCP radio monitoring is intended for trusted local installations only.
- The link and resilience models are illustrative graph analyses, **not** calibrated RF propagation or actual Meshtastic routing behavior.

## Release checklist
- [ ] GitHub Actions tests pass on the final release commit
- [ ] Verify network routes update with offline nodes
- [ ] Verify summary metrics agree with the resilience tab
- [ ] Verify all four tabs and exports on mobile and desktop
- [ ] Verify hosted deployment at https://meshlab.streamlit.app/
- [ ] Publish a GitHub release tagged `v1.1.0` after merge
