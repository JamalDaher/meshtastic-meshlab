# MeshLab v1.0 release candidate

## Highlights
- Simulation-first dashboard with synthetic mesh topology, routes and signal metrics
- Interactive node-outage resilience analysis and critical bridge detection
- Reproducible event timeline and single-node reliability comparisons
- CSV exports and portable deterministic JSON simulation reports
- Streamlined simulation sidebar and refreshed README
- Experimental local USB/TCP Meshtastic metadata monitoring

## Limitations
- Physical radio compatibility has not been validated.
- Simulation is illustrative graph analysis, not validated RF coverage or Meshtastic packet routing.
- No live radio dashboard should be exposed publicly.

## Validation
Run `python -m pytest -q` and verify GitHub Actions before merging or publishing a release.
