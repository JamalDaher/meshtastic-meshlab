# MeshLab v1.2.0 — Advanced RF Planning

Release candidate. Publish the GitHub release only after CI and hosted smoke tests pass.

## Highlights
- Independent ideal free-space path-loss and RF link-budget explorer
- Optional RF-derived network connectivity, with configurable frequency, power, antenna gains, cable loss, receiver sensitivity and synthetic-distance scale
- RF link-margin colors and hover labels on the network topology
- Versioned RF scenario JSON, deterministic RF reports, and one-click preset application
- Legacy distance-threshold simulator, scenarios and reports retained

## Model boundaries
- Coordinates are synthetic; km-per-coordinate-unit is an assumption, not a geospatial map.
- Free-space calculations omit terrain, vegetation, obstructions, multipath, fading, interference, antenna orientation, duty cycle and LoRa packet delivery.
- RF connectivity is a receiver-sensitivity threshold, **not** a measured reliability or coverage prediction.
- RF exports are separate from legacy distance-model exports. Timeline and range comparison remain illustrative and are not RF-profile-aware.
- Hosted Streamlit mode is simulation only. Physical Meshtastic radio support remains experimental and unverified.

## Release checklist
- [ ] GitHub Actions succeeds on final merge commit
- [ ] Test both connectivity modes and all four tabs
- [ ] Adjust receiver sensitivity and verify links change
- [ ] Confirm RF margin colors and hover details; test offline nodes
- [ ] Export RF preset, modify settings, upload and apply; verify settings restored
- [ ] Export RF report and confirm settings, links and margins are present
- [ ] Verify legacy scenario/report exports still work
- [ ] Smoke-test hosted app at https://meshlab.streamlit.app/ on mobile and desktop
- [ ] Publish GitHub release tagged `v1.2.0` after merge
