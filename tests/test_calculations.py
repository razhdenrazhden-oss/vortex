from app.calculations import calculate_metrics


def test_calculate_metrics_increases_with_tss():
    atl, ctl, tsb, readiness = calculate_metrics(prev_atl=0.0, prev_ctl=0.0, today_tss=70.0)
    assert atl > ctl
    assert tsb < 0
    assert 0 <= readiness <= 100


def test_readiness_clamped_bounds():
    _, _, _, readiness_low = calculate_metrics(prev_atl=1000.0, prev_ctl=0.0, today_tss=0.0)
    _, _, _, readiness_high = calculate_metrics(prev_atl=0.0, prev_ctl=1000.0, today_tss=0.0)
    assert readiness_low == 0.0
    assert readiness_high == 100.0
