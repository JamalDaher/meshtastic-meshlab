from meshlab.rf_coverage import margin_category, margin_color, coverage_summary

def test_margin_boundaries():
    assert margin_category(-0.1) == "below sensitivity"
    assert margin_category(0) == "low margin"
    assert margin_category(5.99) == "low margin"
    assert margin_category(6) == "moderate margin"
    assert margin_category(15) == "high margin"

def test_colors_are_defined():
    assert margin_color(2) != margin_color(20)

def test_coverage_counts():
    links = [{"link_margin_db": m} for m in (1, 8, 20, 30)]
    assert coverage_summary(links) == {"low margin": 1, "moderate margin": 1, "high margin": 2}
