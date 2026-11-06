"""Ideal free-space RF link-budget estimates (not terrain-aware LoRa predictions)."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class RadioProfile:
    frequency_mhz: float = 906.875
    tx_power_dbm: float = 22.0
    tx_gain_dbi: float = 2.0
    rx_gain_dbi: float = 2.0
    cable_loss_db: float = 0.0
    receiver_sensitivity_dbm: float = -130.0

    def __post_init__(self):
        values = (self.frequency_mhz, self.tx_power_dbm, self.tx_gain_dbi,
                  self.rx_gain_dbi, self.cable_loss_db, self.receiver_sensitivity_dbm)
        if not all(math.isfinite(v) for v in values):
            raise ValueError("Radio profile values must be finite")
        if self.frequency_mhz <= 0 or self.cable_loss_db < 0:
            raise ValueError("Frequency must be positive and cable loss nonnegative")

def free_space_path_loss(distance_km: float, frequency_mhz: float) -> float:
    """FSPL in dB with distance in km and frequency in MHz."""
    if not math.isfinite(distance_km) or not math.isfinite(frequency_mhz):
        raise ValueError("Distance and frequency must be finite")
    if distance_km <= 0 or frequency_mhz <= 0:
        raise ValueError("Distance and frequency must be positive")
    return 32.44 + 20 * math.log10(distance_km) + 20 * math.log10(frequency_mhz)

def link_budget(distance_km: float, profile: RadioProfile) -> dict:
    loss = free_space_path_loss(distance_km, profile.frequency_mhz)
    received = (profile.tx_power_dbm + profile.tx_gain_dbi + profile.rx_gain_dbi
                - profile.cable_loss_db - loss)
    margin = received - profile.receiver_sensitivity_dbm
    return {"distance_km": distance_km, "path_loss_db": round(loss, 2),
            "received_power_dbm": round(received, 2), "link_margin_db": round(margin, 2),
            "above_sensitivity": margin >= 0}
