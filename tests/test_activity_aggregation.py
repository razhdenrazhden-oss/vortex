from datetime import date

from app.activity_aggregation import (
    classify_workout,
    load_state_from_tsb,
    normalize_units,
    recompute_form_points,
)


def test_normalize_units_converts_to_km_min():
    km, mins = normalize_units(distance_m=12345, duration_s=3660)
    assert km == 12.345
    assert mins == 61.0


def test_load_state_color_mapping_rules():
    assert load_state_from_tsb(-20) == "overreaching"
    assert load_state_from_tsb(-10) == "maintaining"
    assert load_state_from_tsb(0) == "progress"
    assert load_state_from_tsb(15) == "detraining"


def test_classify_workout_skeleton():
    assert classify_workout(distance_km=30, avg_power_w=280, duration_min=70) == "power"
    assert classify_workout(distance_km=90, avg_power_w=180, duration_min=200) == "endurance"
    assert classify_workout(distance_km=15, avg_power_w=120, duration_min=35) == "recovery"


def test_recompute_form_points_returns_year_series_shape():
    points = recompute_form_points({date(2026, 1, 1): 100.0}, start=date(2026, 1, 1), end=date(2026, 1, 3))
    assert len(points) == 3
    assert points[0]["date"].isoformat() == "2026-01-01"
    assert {"atl", "ctl", "tsb", "load_state"}.issubset(points[0].keys())
