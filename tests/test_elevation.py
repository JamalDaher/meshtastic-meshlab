import pytest
from meshlab.elevation import sample_geographic_path, fetch_elevations

def test_path_samples_endpoints():
    samples = sample_geographic_path(34, -88, 35, -88, points=5)
    assert len(samples) == 5
    assert samples[0]["lat"] == pytest.approx(34)
    assert samples[-1]["lat"] == pytest.approx(35)
    assert samples[0]["distance_km"] == 0
    assert samples[-1]["distance_km"] > 100

def test_antimeridian_short_path():
    samples = sample_geographic_path(0, 179, 0, -179)
    assert samples[-1]["distance_km"] < 300

def test_invalid_path():
    with pytest.raises(ValueError):
        sample_geographic_path(34, -88, 34, -88)
    with pytest.raises(ValueError):
        sample_geographic_path(34, -88, 35, -88, points=1)

def test_elevation_adapter_mock(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
    def fake_open(req, timeout):
        assert "latitude=" in req.full_url
        return Response()
    monkeypatch.setattr("meshlab.elevation.urlopen", fake_open)
    monkeypatch.setattr("meshlab.elevation.json.load", lambda _: {"elevation": [100, 110]})
    path = sample_geographic_path(34, -88, 34.01, -88, points=2)
    assert fetch_elevations(path) == [(0.0, 100.0), (round(path[1]["distance_km"], 6), 110.0)]
