"""Geodesic path samples and optional public elevation service adapter.

Elevation is retrieved only when explicitly requested by the user.
"""
import json
import math
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from meshlab.geo import great_circle_km

ELEVATION_ENDPOINT = "https://api.open-meteo.com/v1/elevation"

def sample_geographic_path(start_lat, start_lon, end_lat, end_lon, points=21):
    if type(points) is not int or not 2 <= points <= 100:
        raise ValueError("points must be an integer between 2 and 100")
    distance = great_circle_km(start_lat, start_lon, end_lat, end_lon)
    if distance <= 0:
        raise ValueError("Node locations must differ")
    p1, p2 = math.radians(start_lat), math.radians(end_lat)
    l1, l2 = math.radians(start_lon), math.radians(end_lon)
    def vec(p, l):
        return (math.cos(p) * math.cos(l), math.cos(p) * math.sin(l), math.sin(p))
    a, b = vec(p1, l1), vec(p2, l2)
    dot = max(-1.0, min(1.0, sum(x*y for x, y in zip(a, b))))
    omega = math.acos(dot)
    results = []
    for i in range(points):
        t = i / (points - 1)
        if omega < 1e-9:
            v = tuple((1-t)*x + t*y for x, y in zip(a, b))
        elif abs(math.sin(omega)) < 1e-9:
            raise ValueError("Antipodal points have ambiguous shortest paths")
        else:
            u, w = math.sin((1-t)*omega)/math.sin(omega), math.sin(t*omega)/math.sin(omega)
            v = tuple(u*x + w*y for x, y in zip(a, b))
        norm = math.sqrt(sum(x*x for x in v))
        x, y, z = (q/norm for q in v)
        results.append({"distance_km": distance*t,
                        "lat": math.degrees(math.atan2(z, math.hypot(x, y))),
                        "lon": math.degrees(math.atan2(y, x))})
    return results

def fetch_elevations(path, timeout=12):
    """Call Open-Meteo elevation API for a validated path, returning meters ASL."""
    if not isinstance(path, list) or not 2 <= len(path) <= 100:
        raise ValueError("Path must contain 2–100 coordinates")
    for p in path:
        if not isinstance(p, dict) or not all(k in p for k in ("lat", "lon", "distance_km")):
            raise ValueError("Invalid path sample")
        great_circle_km(p["lat"], p["lon"], p["lat"], p["lon"])
    params = urlencode({"latitude": ",".join(f'{p["lat"]:.6f}' for p in path),
                        "longitude": ",".join(f'{p["lon"]:.6f}' for p in path)})
    req = Request(ELEVATION_ENDPOINT + "?" + params, headers={"User-Agent": "MeshLab/1.3"})
    with urlopen(req, timeout=timeout) as response:
        payload = json.load(response)
    heights = payload.get("elevation")
    if not isinstance(heights, list) or len(heights) != len(path):
        raise ValueError("Elevation service returned incomplete data")
    if any(type(h) not in (int, float) or not math.isfinite(h) for h in heights):
        raise ValueError("Elevation service returned invalid elevation values")
    return [(round(p["distance_km"], 6), float(h)) for p, h in zip(path, heights)]
