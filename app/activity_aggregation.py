from datetime import date, timedelta


def normalize_units(distance_m: float | None, duration_s: float | None) -> tuple[float, float]:
    return (round((distance_m or 0.0) / 1000.0, 3), round((duration_s or 0.0) / 60.0, 2))


def load_state_from_tsb(tsb: float) -> str:
    if tsb <= -15:
        return "overreaching"
    if tsb < -5:
        return "maintaining"
    if tsb <= 10:
        return "progress"
    return "detraining"


def classify_workout(distance_km: float, avg_power_w: float | None, duration_min: float) -> str:
    if avg_power_w and avg_power_w >= 260:
        return "power"
    if distance_km >= 80 or duration_min >= 180:
        return "endurance"
    if duration_min < 45:
        return "recovery"
    return "mixed"


def recompute_form_points(activities_by_day: dict[date, float], start: date, end: date) -> list[dict]:
    atl = 0.0
    ctl = 0.0
    points: list[dict] = []
    current = start
    while current <= end:
        day_load = activities_by_day.get(current, 0.0)
        atl = atl + (day_load - atl) / 7
        ctl = ctl + (day_load - ctl) / 42
        tsb = ctl - atl
        points.append(
            {
                "date": current,
                "atl": round(atl, 2),
                "ctl": round(ctl, 2),
                "tsb": round(tsb, 2),
                "load_state": load_state_from_tsb(tsb),
            }
        )
        current += timedelta(days=1)
    return points
