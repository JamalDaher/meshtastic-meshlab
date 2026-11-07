import pytest
from meshlab.height_planner import sweep_antenna_heights

def test_finds_clear_height():
    samples=[(0,100),(0.5,100),(1,100)]
    rows=sweep_antenna_heights(samples,2,2,906.875,0.6,20,1)
    assert rows[0]["fresnel_clear"] is False
    assert rows[-1]["fresnel_clear"] is True
    assert rows[-1]["raise_both_by_m"] > 0

def test_already_clear():
    rows=sweep_antenna_heights([(0,100),(0.5,100),(1,100)],30,30,906.875)
    assert len(rows)==1
    assert rows[0]["fresnel_clear"]

def test_unreachable_within_limit():
    rows=sweep_antenna_heights([(0,100),(0.5,100),(1,100)],1,1,906.875,max_height_m=2)
    assert not rows[-1]["fresnel_clear"]

def test_invalid_step():
    with pytest.raises(ValueError):
        sweep_antenna_heights([(0,0),(1,0)],2,2,906.875,step_m=0)
