from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.main import recompute_metrics_from
from app.models import Base, DailyMetrics, Workout


def test_recompute_fills_rest_days_with_zero_tss():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, future=True)

    with SessionLocal() as db:
        db.add_all(
            [
                Workout(workout_date=date(2026, 1, 1), tss=100),
                Workout(workout_date=date(2026, 1, 3), tss=50),
            ]
        )
        db.flush()

        recompute_metrics_from(db=db, from_date=date(2026, 1, 1))
        db.commit()

        metrics = list(db.scalars(select(DailyMetrics).order_by(DailyMetrics.metric_date.asc())).all())

    assert [m.metric_date.isoformat() for m in metrics] == ["2026-01-01", "2026-01-02", "2026-01-03"]
    assert metrics[1].tss == 0.0


def test_recompute_updates_existing_rows_in_place():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, future=True)

    with SessionLocal() as db:
        db.add(Workout(workout_date=date(2026, 1, 2), tss=40))
        db.flush()
        recompute_metrics_from(db=db, from_date=date(2026, 1, 2))
        db.flush()

        initial_metric = db.scalar(select(DailyMetrics).where(DailyMetrics.metric_date == date(2026, 1, 2)))
        initial_id = initial_metric.id

        db.add(Workout(workout_date=date(2026, 1, 2), tss=10))
        db.flush()
        recompute_metrics_from(db=db, from_date=date(2026, 1, 2))
        db.commit()

        updated_metric = db.scalar(select(DailyMetrics).where(DailyMetrics.metric_date == date(2026, 1, 2)))

    assert updated_metric.id == initial_id
    assert updated_metric.tss == 50.0
