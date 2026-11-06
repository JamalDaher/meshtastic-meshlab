import math
import pytest
from meshlab.rf import RadioProfile, free_space_path_loss, link_budget

def test_fspl_known_reference():
    assert free_space_path_loss(1, 1000) == pytest.approx(92.44, abs=0.01)

def test_distance_doubling_adds_six_db():
    assert free_space_path_loss(2, 900) - free_space_path_loss(1, 900) == pytest.approx(20 * math.log10(2))

def test_link_budget_accounting():
    p = RadioProfile(frequency_mhz=1000, tx_power_dbm=20, tx_gain_dbi=3,
                     rx_gain_dbi=2, cable_loss_db=1, receiver_sensitivity_dbm=-100)
    b = link_budget(1, p)
    assert b["path_loss_db"] == pytest.approx(92.44)
    assert b["received_power_dbm"] == pytest.approx(-68.44)
    assert b["link_margin_db"] == pytest.approx(31.56)
    assert b["above_sensitivity"]

@pytest.mark.parametrize("distance,frequency", [(0, 900), (-1, 900), (1, 0), (float("nan"), 900)])
def test_invalid_fspl_inputs(distance, frequency):
    with pytest.raises(ValueError):
        free_space_path_loss(distance, frequency)

def test_invalid_radio_profile():
    with pytest.raises(ValueError):
        RadioProfile(cable_loss_db=-1)
