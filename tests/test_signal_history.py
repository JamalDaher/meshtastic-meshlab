from meshlab.signal_history import comparison_series

def test_filters_sorts_and_ignores_missing():
    events=[
      {"node":"A","time":"2026-11-07T12:02:00+00:00","snr":2,"rssi":-95},
      {"node":"B","time":"2026-11-07T12:01:00+00:00","snr":4,"rssi":-90},
      {"node":"A","time":"bad","snr":5},
      {"node":"A","time":"2026-11-07T12:03:00+00:00","snr":None}]
    rows=comparison_series(events,["A","B"],"snr")
    assert [r["node"] for r in rows]==["B","A"]
    assert comparison_series(events,["A"],"rssi")[0]["reading"]==-95

def test_bounds_and_invalid_metric():
    events=[{"node":"A","time":f"2026-11-07T12:00:{i:02d}+00:00","snr":i} for i in range(3)]
    assert len(comparison_series(events,max_points=2))==2
    try:
        comparison_series([],metric="battery")
        assert False
    except ValueError:
        pass
