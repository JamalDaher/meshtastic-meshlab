"""Classify ideal RF link margins for network visualization."""
def margin_category(margin_db: float) -> str:
    if margin_db < 0:
        return "below sensitivity"
    if margin_db < 6:
        return "low margin"
    if margin_db < 15:
        return "moderate margin"
    return "high margin"

def margin_color(margin_db: float) -> str:
    return {"below sensitivity": "#777777", "low margin": "#e85d5d",
            "moderate margin": "#eab54f", "high margin": "#36b6a0"}[margin_category(margin_db)]

def coverage_summary(links: list[dict]) -> dict:
    counts = {"low margin": 0, "moderate margin": 0, "high margin": 0}
    for link in links:
        category = margin_category(link["link_margin_db"])
        if category in counts:
            counts[category] += 1
    return counts
