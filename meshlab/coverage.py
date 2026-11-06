"""Ideal free-space sensitivity-radius and geographic ring calculations."""
import math
from meshlab.rf import RadioProfile, link_budget

def theoretical_radius_km(profile=None, reserve_margin_db=0.0):
    """Radius where ideal free-space received power reaches sensitivity + reserve."""
    profile = profile or RadioProfile()
    if not math.isfinite(reserve_margin_db) or reserve_margin_db < 0:
        raise ValueError("Reserve margin must be finite and nonnegative")
    allowable_loss = (profile.tx_power_dbm + profile.tx_gain_dbi + profile.rx_gain_dbi
                      - profile.cable_loss_db - profile.receiver_sensitivity_dbm
                      - reserve_margin_db)
    exponent = (allowable_loss - 32.44 - 20 * math.log10(profile.frequency_mhz)) / 20
    if exponent > 300:
        raise ValueError("Theoretical radius exceeds numeric limits")
    return 10 ** exponent

def coverage_ring(lat, lon, radius_km, points=72):
    """Geodesic circle points on a spherical Earth; suitable for visualization only."""
    if not all(math.isfinite(v) for v in (lat, lon, radius_km)):
        raise ValueError("Coordinates and radius must be finite")
    if not -90 <= lat <= 90 or not -180 <= lon <= 180 or radius_km <= 0:
        raise ValueError("Invalid circle center or radius")
    if not isinstance(points, int) or not 12 <= points <= 720:
        raise ValueError("points must be between 12 and 720")
    angular = radius_km / 6371.0088
    if angular >= math.pi:
        raise ValueError("Radius too large to draw as a geographic ring")
    phi, lam = math.radians(lat), math.radians(lon)
    coords = []
    for i in range(points + 1):
        bearing = 2 * math.pi * i / points
        next_phi = math.asin(max(-1.0, min(1.0,
            math.sin(phi) * math.cos(angular) + math.cos(phi) * math.sin(angular) * math.cos(bearing))))
        next_lam = lam + math.atan2(math.sin(bearing) * math.sin(angular) * math.cos(phi),
                                    math.cos(angular) - math.sin(phi) * math.sin(next_phi))
        wrapped_lon = (math.degrees(next_lam) + 180) % 360 - 180
        coords.append((math.degrees(next_phi), wrapped_lon))
    return coords
