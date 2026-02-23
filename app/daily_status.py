from typing import Any


def readiness_from_tsb(tsb: float) -> float:
    """Normalize TSB to readiness in [0, 100]."""
    return max(0.0, min(100.0, 50.0 + (tsb / 30.0) * 50.0))


def fatigue_level_from_tsb(tsb: float) -> str:
    if tsb <= -20:
        return "high"
    if tsb <= -5:
        return "moderate"
    return "low"


def upsert_daily_status(
    existing: Any,
    *,
    user_id: int,
    status_date,
    readiness_score: float,
    tsb: float,
):
    fatigue_level = fatigue_level_from_tsb(tsb)
    if existing:
        existing.readiness_score = readiness_score
        existing.tsb = tsb
        existing.fatigue_level = fatigue_level
        return existing

    # Imported lazily to keep utility functions testable without SQLAlchemy runtime.
    from app.models import DailyStatus

    return DailyStatus(
        user_id=user_id,
        status_date=status_date,
        readiness_score=readiness_score,
        fatigue_level=fatigue_level,
        tsb=tsb,
    )
