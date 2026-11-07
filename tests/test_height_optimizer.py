from meshlab.height_planner import optimize_independent_heights

def test_independent_search_finds_clear_configuration():
    rows = optimize_independent_heights([(0,100),(0.5,100),(1,100)], 2, 2, 906.875,
                                        max_height_m=20, step_m=1)
    assert rows
    assert rows[0]["total_added_m"] <= 20
    assert rows == sorted(rows, key=lambda x: (x["total_added_m"],
                                               abs(x["tx_added_m"]-x["rx_added_m"]),
                                               x["tx_height_m"], x["rx_height_m"]))

def test_no_feasible_configuration():
    assert optimize_independent_heights([(0,100),(0.5,100),(1,100)], 1, 1, 906.875,
                                        max_height_m=2, step_m=1) == []

def test_existing_clear_is_zero_added():
    rows = optimize_independent_heights([(0,100),(0.5,100),(1,100)], 30, 30, 906.875,
                                        max_height_m=30)
    assert rows[0]["total_added_m"] == 0
