"""Geographic node planning with great-circle distance and ideal RF estimates."""
import math
from meshlab.rf import RadioProfile, link_budget

EARTH_RADIUS_KM = 6371.0088

def validate_nodes(nodes):
    if not isinstance(nodes, list) or not 2 <= len(nodes) <= 30:
        raise ValueError("Provide between 2 and 30 geographic nodes")
    seen = set()
    cleaned = []
    for node in nodes:
        if not isinstance(node, dict) or set(node) != {"name", "lat", "lon"}:
            raise ValueError("Each node needs name, lat and lon")
        name, lat, lon = node["name"], node["lat"], node["lon"]
        if not isinstance(name, str) or not name.strip() or len(name) > 80 or name in seen:
            raise ValueError("Node names must be unique and nonempty")
        if type(lat) not in (float, int) or type(lon) not in (float, int):
            raise ValueError("Latitude and longitude must be numeric")
        if not all(math.isfinite(v) for v in (lat, lon)) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
            raise ValueError("Invalid geographic coordinates")
        seen.add(name)
        cleaned.append({"name": name, "lat": float(lat), "lon": float(lon)})
    return cleaned

def great_circle_km(lat1, lon1, lat2, lon2):
    if not all(math.isfinite(v) for v in (lat1, lon1, lat2, lon2)):
        raise ValueError("Coordinates must be finite")
    if any(abs(lat) > 90 for lat in (lat1, lat2)) or any(abs(lon) > 180 for lon in (lon1, lon2)):
        raise ValueError("Invalid geographic coordinates")
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(min(1.0, math.sqrt(a)))

def geographic_links(nodes, profile=None):
    nodes = validate_nodes(nodes)
    profile = profile or RadioProfile()
    results = []
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            distance = great_circle_km(a["lat"], a["lon"], b["lat"], b["lon"])
            budget = link_budget(max(distance, 0.001), profile)
            results.append({"source": a["name"], "target": b["name"],
                            "distance_km": round(distance, 3),
                            "received_power_dbm": budget["received_power_dbm"],
                            "link_margin_db": budget["link_margin_db"],
                            "above_sensitivity": budget["above_sensitivity"]})
    return results
