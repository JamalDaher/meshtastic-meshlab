# MeshLab v1.3.0 — Geographic RF Planning

## Highlights

MeshLab v1.3 adds a dedicated **Geographic** workspace for planning proposed Meshtastic-style radio links on a map, comparing idealized RF margins, evaluating sampled terrain and Fresnel-zone clearance, and exploring antenna heights.

- Enter 2–30 geographic nodes and review pairwise great-circle distances, free-space link budgets, and mapped RF links.
- Explore illustrative coverage rings, separately from theoretical free-space sensitivity radii.
- Manually enter terrain profiles or explicitly fetch elevation samples from Open-Meteo for a selected link.
- Evaluate geometric line of sight with approximate 4/3-Earth-radius curvature and first Fresnel-zone clearance at sampled points.
- Save fetched profiles per geographic link for session-only comparison. Links without data remain **Not evaluated**.
- Compare sites using ideal free-space estimates and separately using evaluated terrain/Fresnel results.
- Sweep equal antenna-height increases or search independent TX/RX height combinations on a bounded discrete grid.
- Export geographic RF planning reports (versioned JSON), site rankings, and link comparisons (CSV).
- Use five workspace tabs to keep the interface navigable on smaller screens.

## Upgrade and validation checklist

1. Run `python -m pytest -q` and confirm the complete test suite passes.
2. Launch `streamlit run app.py`; confirm all five tabs render and geographic node editing works.
3. Enter at least three sites; inspect map, RF links, ideal site rankings, and coverage-ring controls.
4. Select two different sites; fetch elevations only after reviewing the Open-Meteo privacy notice. Confirm the sampled terrain and Fresnel charts update.
5. Save a fetched link profile; select another pair and confirm its status is **Not evaluated** until separately fetched and saved.
6. Compare saved links, adjust antenna heights and Fresnel threshold, and verify site comparisons update.
7. Test equal-height sweep and independent TX/RX search, including no-feasible-solution cases.
8. Download and inspect geographic report JSON and CSV exports. Confirm assumptions, missing-data statuses, and node/link counts.
9. Check the mobile layout, especially expandable tables and terrain controls.
10. Confirm the hosted Streamlit deployment is healthy before publishing the GitHub release.

## Modeling limitations

This is an **illustrative planning tool**, not a calibrated LoRa coverage or deployment certification system. Ideal free-space budgets omit terrain loss, foliage/building clutter, multipath, interference, antenna patterns, weather, and measured packet delivery. Terrain and Fresnel checks depend on sparse sampled elevations and a simplified effective-Earth-radius approximation; diffraction and clutter are not modeled. Coverage rings are not guaranteed coverage. Antenna-height optimization minimizes a discrete height metric, not construction cost or engineering risk. Missing terrain assessments are never treated as clear.

## Privacy and data

Open-Meteo elevation lookup is opt-in; selected geographic coordinates are sent to the provider only when the user requests a fetch. Saved terrain profiles are Streamlit-session-only. Geographic JSON reports include site coordinates and analysis results, but not raw elevation samples. Review exports before sharing them.

## Release procedure

After the checklist passes and documentation PR is merged, publish tag `v1.3.0` from the latest main commit and use these notes as the GitHub release description. Do not tag before CI and deployment checks pass.
