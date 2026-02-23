from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.main import recompute_metrics_from
from app.models import Base, DailyMetrics, User, Workout


def test_recompute_fills_rest_days_with_zero_tss_per_user():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, future=True)

    with SessionLocal() as db:
        db.add_all(
            [
                User(id=1),
                User(id=2),
                Workout(user_id=1, workout_date=date(2026, 1, 1), tss=100),
                Workout(user_id=1, workout_date=date(2026, 1, 3), tss=50),
                Workout(user_id=2, workout_date=date(2026, 1, 2), tss=90),
            ]
        )
        db.flush()

        recompute_metrics_from(db=db, user_id=1, from_date=date(2026, 1, 1))
        db.commit()

        metrics_user_1 = list(
            db.scalars(
                select(DailyMetrics)
                .where(DailyMetrics.user_id == 1)
                .order_by(DailyMetrics.metric_date.asc())
            ).all()
        )
        metrics_user_2 = list(
            db.scalars(
                select(DailyMetrics)
                .where(DailyMetrics.user_id == 2)
                .order_by(DailyMetrics.metric_date.asc())
            ).all()
        )

    assert [m.metric_date.isoformat() for m in metrics_user_1] == ["2026-01-01", "2026-01-02", "2026-01-03"]
    assert metrics_user_1[1].tss == 0.0
    assert metrics_user_2 == []


def test_recompute_updates_existing_rows_in_place_for_same_user_and_day():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, future=True)

    with SessionLocal() as db:
        db.add_all([User(id=1), Workout(user_id=1, workout_date=date(2026, 1, 2), tss=40)])
        db.flush()
        recompute_metrics_from(db=db, user_id=1, from_date=date(2026, 1, 2))
        db.flush()

        initial_metric = db.scalar(
            select(DailyMetrics).where(DailyMetrics.user_id == 1, DailyMetrics.metric_date == date(2026, 1, 2))
        )
        initial_id = initial_metric.id

        db.add(Workout(user_id=1, workout_date=date(2026, 1, 2), tss=10))
        db.flush()
        recompute_metrics_from(db=db, user_id=1, from_date=date(2026, 1, 2))
        db.commit()

        updated_metric = db.scalar(
            select(DailyMetrics).where(DailyMetrics.user_id == 1, DailyMetrics.metric_date == date(2026, 1, 2))
        )

    assert updated_metric.id == initial_id
    assert updated_metric.tss == 50.0


def test_recompute_trims_stale_tail_when_latest_workout_removed_or_shifted():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, future=True)

    with SessionLocal() as db:
        db.add_all(
            [
                User(id=1),
                Workout(user_id=1, workout_date=date(2026, 1, 1), tss=40),
                Workout(user_id=1, workout_date=date(2026, 1, 3), tss=60),
            ]
        )
        db.flush()
        recompute_metrics_from(db=db, user_id=1, from_date=date(2026, 1, 1))
        db.flush()

        # Remove latest workout day and recompute from that date.
        latest_workout = db.scalar(
            select(Workout).where(Workout.user_id == 1, Workout.workout_date == date(2026, 1, 3)).limit(1)
        )
        db.delete(latest_workout)
        db.flush()
        recompute_metrics_from(db=db, user_id=1, from_date=date(2026, 1, 3))
        db.commit()

        metric_dates = [
            d.isoformat()
            for d in db.scalars(
                select(DailyMetrics.metric_date).where(DailyMetrics.user_id == 1).order_by(DailyMetrics.metric_date.asc())
            ).all()
        ]

    assert metric_dates == ["2026-01-01"]
