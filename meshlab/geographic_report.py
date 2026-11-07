"""Versioned, inspectable geographic planning report."""
import json
from datetime import datetime, timezone
from meshlab.site_comparison import rank_sites
from meshlab.site_terrain import summarize_saved_links
from meshlab.terrain_ranking import rank_terrain_sites

def build_geographic_report(nodes, links, saved_profiles, tx_height_m, rx_height_m,
                            frequency_mhz, clearance_fraction, radio_profile):
    comparisons = summarize_saved_links(nodes, links, saved_profiles, tx_height_m,
                                        rx_height_m, frequency_mhz, clearance_fraction)
    return {
        "schema_version": "meshlab-geographic-report-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "assumptions": {
            "radio_profile": dict(radio_profile),
            "tx_antenna_height_m": tx_height_m,
            "rx_antenna_height_m": rx_height_m,
            "fresnel_frequency_mhz": frequency_mhz,
            "required_fresnel_fraction": clearance_fraction,
            "terrain_model": "sampled-elevation-effective-earth-radius-4/3",
            "rf_model": "ideal-free-space-sensitivity-threshold"},
        "nodes": nodes,
        "rf_links": links,
        "ideal_site_ranking": rank_sites(nodes, links),
        "terrain_link_assessments": comparisons,
        "terrain_site_ranking": rank_terrain_sites(nodes, links, comparisons),
        "limitations": [
            "No measured packet delivery, fading, interference, clutter, diffraction or antenna patterns.",
            "Terrain/Fresnel status applies only at sampled elevations.",
            "Missing terrain is Not evaluated and must not be treated as clear.",
            "Site rankings are planning indicators, not verified deployment recommendations.",
            "No private elevation samples are included; assessments are recalculated from session profiles."
        ],
    }

def report_json(report):
    return json.dumps(report, indent=2, allow_nan=False)
