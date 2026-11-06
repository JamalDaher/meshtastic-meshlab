"""Terrain line-of-sight evaluation from externally supplied elevation samples.

This module does not fetch terrain. Elevations must be meters above sea level.
"""
import math

EARTH_RADIUS_M = 6371008.8

def analyze_terrain_profile(samples, tx_height_m=2.0, rx_height_m=2.0,
                            effective_earth_radius_factor=4.0 / 3.0):
    """Return geometric terrain clearance with approximate Earth curvature.

    samples: ordered (distance_km, ground_elevation_m) pairs, including endpoints.
    The straight sightline joins antenna heights above the endpoint ground.
    Positive clearance means unobstructed geometric line of sight.
    """
    if not isinstance(samples, (list, tuple)) or len(samples) < 2:
        raise ValueError("At least two elevation samples are required")
    for v in (tx_height_m, rx_height_m, effective_earth_radius_factor):
        if type(v) not in (int, float) or not math.isfinite(v):
            raise ValueError("Heights and Earth-radius factor must be finite numbers")
    if tx_height_m < 0 or rx_height_m < 0 or effective_earth_radius_factor <= 0:
        raise ValueError("Heights must be nonnegative and Earth-radius factor positive")
    parsed = []
    for sample in samples:
        if not isinstance(sample, (list, tuple)) or len(sample) != 2:
            raise ValueError("Each sample must contain distance_km and elevation_m")
        distance, elevation = sample
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in (distance, elevation)):
            raise ValueError("Sample values must be finite numbers")
        parsed.append((float(distance), float(elevation)))
    if abs(parsed[0][0]) > 1e-9 or parsed[-1][0] <= 0:
        raise ValueError("Samples must start at 0 km and end at positive distance")
    if any(b[0] <= a[0] for a, b in zip(parsed, parsed[1:])):
        raise ValueError("Sample distances must increase strictly")
    total_m = parsed[-1][0] * 1000
    tx_alt = parsed[0][1] + tx_height_m
    rx_alt = parsed[-1][1] + rx_height_m
    evaluated = []
    for distance_km, ground_m in parsed:
        x = distance_km * 1000
        sightline_m = tx_alt + (rx_alt - tx_alt) * x / total_m
        bulge_m = x * (total_m - x) / (2 * effective_earth_radius_factor * EARTH_RADIUS_M)
        clearance_m = sightline_m - ground_m - bulge_m
        evaluated.append({"distance_km": distance_km, "terrain_elevation_m": ground_m,
                          "sightline_elevation_m": round(sightline_m, 3),
                          "curvature_bulge_m": round(bulge_m, 3),
                          "clearance_m": round(clearance_m, 3)})
    interior = evaluated[1:-1]
    minimum = min((s["clearance_m"] for s in interior), default=min(tx_height_m, rx_height_m))
    return {"distance_km": parsed[-1][0], "clear_line_of_sight": minimum > 0,
            "minimum_interior_clearance_m": round(minimum, 3),
            "samples": evaluated,
            "model": "geometric-terrain-los-effective-earth-radius"}
