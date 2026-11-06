"""First Fresnel-zone clearance for sampled terrain profiles.

Approximate pointwise analysis, not a propagation or diffraction model.
"""
import math

SPEED_OF_LIGHT_M_S = 299792458.0

def analyze_fresnel_clearance(terrain_result, frequency_mhz=906.875, clearance_fraction=0.6):
    if not isinstance(terrain_result, dict) or not isinstance(terrain_result.get("samples"), list):
        raise ValueError("A terrain analysis result is required")
    if len(terrain_result["samples"]) < 2:
        raise ValueError("At least two samples are required")
    if type(frequency_mhz) not in (int, float) or not math.isfinite(frequency_mhz) or frequency_mhz <= 0:
        raise ValueError("Frequency must be finite and positive")
    if type(clearance_fraction) not in (int, float) or not math.isfinite(clearance_fraction) or not 0 <= clearance_fraction <= 1:
        raise ValueError("Clearance fraction must be between zero and one")
    total = terrain_result["samples"][-1]["distance_km"] * 1000
    if not math.isfinite(total) or total <= 0:
        raise ValueError("Path distance must be positive")
    wavelength = SPEED_OF_LIGHT_M_S / (frequency_mhz * 1e6)
    results = []
    for sample in terrain_result["samples"]:
        d1 = sample["distance_km"] * 1000
        d2 = total - d1
        if not 0 <= d1 <= total:
            raise ValueError("Sample distance outside path")
        radius = math.sqrt(wavelength * d1 * d2 / total)
        required = clearance_fraction * radius
        actual = sample["clearance_m"]
        results.append({**sample, "fresnel_radius_m": round(radius, 3),
                        "required_clearance_m": round(required, 3),
                        "fresnel_clearance_margin_m": round(actual - required, 3)})
    interior = results[1:-1]
    minimum = min((r["fresnel_clearance_margin_m"] for r in interior),
                  default=min(results[0]["fresnel_clearance_margin_m"],
                              results[-1]["fresnel_clearance_margin_m"]))
    return {"frequency_mhz": frequency_mhz, "clearance_fraction": clearance_fraction,
            "minimum_fresnel_margin_m": round(minimum, 3),
            "fresnel_clear": minimum > 0, "samples": results}
