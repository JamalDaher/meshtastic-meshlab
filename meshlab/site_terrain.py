"""Session-only terrain profiles associated with exact geographic endpoints."""

def link_key(a, b):
    """Direction-independent key, including coordinates to avoid stale site reuse."""
    endpoints = []
    for node in (a, b):
        endpoints.append((str(node["name"]), float(node["lat"]), float(node["lon"])))
    if endpoints[0] == endpoints[1]:
        raise ValueError("Select two distinct sites")
    return tuple(sorted(endpoints))

def summarize_saved_links(nodes, links, saved, tx_height_m, rx_height_m,
                          frequency_mhz, clearance_fraction):
    from meshlab.terrain import analyze_terrain_profile
    from meshlab.fresnel import analyze_fresnel_clearance
    by_name = {node["name"]: node for node in nodes}
    rows = []
    for link in links:
        key = link_key(by_name[link["source"]], by_name[link["target"]])
        samples = saved.get(key)
        row = {"source": link["source"], "target": link["target"],
               "distance_km": link["distance_km"],
               "rf_margin_db": link["link_margin_db"],
               "terrain_status": "Not evaluated",
               "fresnel_status": "Not evaluated",
               "minimum_fresnel_margin_m": None}
        if samples is not None:
            try:
                terrain = analyze_terrain_profile(samples, tx_height_m, rx_height_m)
                fresnel = analyze_fresnel_clearance(terrain, frequency_mhz, clearance_fraction)
                row.update(terrain_status="Clear" if terrain["clear_line_of_sight"] else "Obstructed",
                           fresnel_status="Clear" if fresnel["fresnel_clear"] else "Insufficient",
                           minimum_fresnel_margin_m=fresnel["minimum_fresnel_margin_m"])
            except (ValueError, TypeError, KeyError):
                row["terrain_status"] = "Invalid saved profile"
                row["fresnel_status"] = "Invalid saved profile"
        rows.append(row)
    return rows
