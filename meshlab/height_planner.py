"""Discrete antenna-height planning over an existing sampled terrain path."""
from meshlab.terrain import analyze_terrain_profile
from meshlab.fresnel import analyze_fresnel_clearance

def sweep_antenna_heights(samples, tx_height_m, rx_height_m, frequency_mhz,
                          clearance_fraction=0.6, max_height_m=30, step_m=1):
    """Raise both endpoints equally in steps; return first sampled-clear result.

    This does not determine a globally minimal two-antenna configuration.
    """
    if step_m <= 0 or max_height_m < max(tx_height_m, rx_height_m):
        raise ValueError("Maximum height must cover current heights and step must be positive")
    if max_height_m > 1000 or step_m < 0.1:
        raise ValueError("Height sweep bounds exceeded")
    rows = []
    steps = int((max_height_m - max(tx_height_m, rx_height_m)) / step_m)
    for i in range(steps + 1):
        delta = i * step_m
        tx = tx_height_m + delta
        rx = rx_height_m + delta
        terrain = analyze_terrain_profile(samples, tx, rx)
        fresnel = analyze_fresnel_clearance(terrain, frequency_mhz, clearance_fraction)
        rows.append({"tx_height_m": round(tx, 2), "rx_height_m": round(rx, 2),
                     "raise_both_by_m": round(delta, 2),
                     "minimum_fresnel_margin_m": fresnel["minimum_fresnel_margin_m"],
                     "fresnel_clear": fresnel["fresnel_clear"]})
        if fresnel["fresnel_clear"]:
            break
    return rows
