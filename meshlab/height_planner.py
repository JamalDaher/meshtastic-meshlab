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

def optimize_independent_heights(samples, tx_height_m, rx_height_m, frequency_mhz,
                                 clearance_fraction=0.6, max_height_m=30, step_m=1):
    """Find minimum total added height on a discrete grid, tie-break by balance.

    Searches nonnegative increments at each endpoint independently. The result
    is grid-optimal only; tower costs, obstructions and antenna constraints vary.
    """
    import math
    for value in (tx_height_m, rx_height_m, frequency_mhz, clearance_fraction, max_height_m, step_m):
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("Inputs must be finite numbers")
    if min(tx_height_m, rx_height_m) < 0 or frequency_mhz <= 0 or not 0 <= clearance_fraction <= 1:
        raise ValueError("Invalid height, frequency or clearance fraction")
    if step_m < 0.5 or max_height_m > 1000 or max_height_m < max(tx_height_m, rx_height_m):
        raise ValueError("Invalid sweep limits")
    tx_steps = int((max_height_m - tx_height_m) / step_m)
    rx_steps = int((max_height_m - rx_height_m) / step_m)
    if (tx_steps + 1) * (rx_steps + 1) > 20000:
        raise ValueError("Too many configurations; increase height step or reduce maximum")
    candidates = []
    for i in range(tx_steps + 1):
        for j in range(rx_steps + 1):
            tx = tx_height_m + i * step_m
            rx = rx_height_m + j * step_m
            terrain = analyze_terrain_profile(samples, tx, rx)
            fresnel = analyze_fresnel_clearance(terrain, frequency_mhz, clearance_fraction)
            if fresnel["fresnel_clear"]:
                candidates.append({
                    "tx_height_m": round(tx, 2), "rx_height_m": round(rx, 2),
                    "tx_added_m": round(i * step_m, 2), "rx_added_m": round(j * step_m, 2),
                    "total_added_m": round((i + j) * step_m, 2),
                    "minimum_fresnel_margin_m": fresnel["minimum_fresnel_margin_m"]})
    candidates.sort(key=lambda row: (row["total_added_m"],
                                    abs(row["tx_added_m"] - row["rx_added_m"]),
                                    row["tx_height_m"], row["rx_height_m"]))
    return candidates[:10]
