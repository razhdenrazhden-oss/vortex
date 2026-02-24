from app.daily_status import fatigue_level_from_tsb, readiness_from_tsb


def test_readiness_bounds():
    assert readiness_from_tsb(-100) == 0.0
    assert readiness_from_tsb(100) == 100.0


def test_fatigue_level_ranges():
    assert fatigue_level_from_tsb(-25) == "high"
    assert fatigue_level_from_tsb(-10) == "moderate"
    assert fatigue_level_from_tsb(0) == "low"
