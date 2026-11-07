from meshlab.signal_quality import signal_quality_summary

def test_summary_ignores_missing_and_nonfinite_readings():
    rows=signal_quality_summary([
        {"node":"A","snr":5,"rssi":-100},
        {"node":"A","snr":-1,"rssi":-110},
        {"node":"A","snr":float("nan"),"rssi":None},
        {"node":"B","snr":None,"rssi":None}])
    assert rows[0]["mean_snr_db"]==2
    assert rows[0]["mean_rssi_dbm"]==-105
    assert rows[0]["snr_samples"]==2
    assert rows[0]["observed_packets"]==3
    assert rows[1]["mean_snr_db"] is None

def test_empty_and_sample_bound():
    assert signal_quality_summary([])==[]
    rows=signal_quality_summary([{"node":"A","snr":i,"rssi":-100} for i in range(5)],max_samples=2)
    assert rows[0]["observed_packets"]==2
