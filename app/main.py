from datetime import date
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.calculations import calculate_metrics
from app.database import SessionLocal, engine
from app.models import Base, DailyMetrics, Workout
from app.schemas import DailyMetricsRead, WorkoutCreate, WorkoutRead

app = FastAPI(title="Activity Load Tracker API", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def recompute_metrics_from(db: Session, from_date: date) -> None:
    prior_metric = db.scalar(
        select(DailyMetrics)
        .where(DailyMetrics.metric_date < from_date)
        .order_by(DailyMetrics.metric_date.desc())
        .limit(1)
    )
    prev_atl = prior_metric.atl if prior_metric else 0.0
    prev_ctl = prior_metric.ctl if prior_metric else 0.0

    affected_dates = list(
        db.scalars(
            select(Workout.workout_date)
            .where(Workout.workout_date >= from_date)
            .group_by(Workout.workout_date)
            .order_by(Workout.workout_date.asc())
        ).all()
    )

    for metric_day in affected_dates:
        day_tss = (
            db.scalar(select(func.coalesce(func.sum(Workout.tss), 0.0)).where(Workout.workout_date == metric_day)) or 0.0
        )
        atl, ctl, tsb, readiness = calculate_metrics(prev_atl=prev_atl, prev_ctl=prev_ctl, today_tss=day_tss)

        metric = db.scalar(select(DailyMetrics).where(DailyMetrics.metric_date == metric_day).limit(1))
        if metric:
            metric.tss = day_tss
            metric.atl = atl
            metric.ctl = ctl
            metric.tsb = tsb
            metric.readiness_score = readiness
        else:
            db.add(
                DailyMetrics(
                    metric_date=metric_day,
                    tss=day_tss,
                    atl=atl,
                    ctl=ctl,
                    tsb=tsb,
                    readiness_score=readiness,
                )
            )

        prev_atl, prev_ctl = atl, ctl


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/workouts", response_model=WorkoutRead, status_code=201)
def create_workout(payload: WorkoutCreate, db: Session = Depends(get_db)) -> Workout:
    workout = Workout(workout_date=payload.workout_date, tss=payload.tss)
    db.add(workout)
    db.flush()

    recompute_metrics_from(db=db, from_date=payload.workout_date)

    db.commit()
    db.refresh(workout)
    return workout


@app.get("/metrics", response_model=list[DailyMetricsRead])
def list_metrics(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[DailyMetrics]:
    query = select(DailyMetrics)
    if start_date:
        query = query.where(DailyMetrics.metric_date >= start_date)
    if end_date:
        query = query.where(DailyMetrics.metric_date <= end_date)
    query = query.order_by(DailyMetrics.metric_date.asc())
    return list(db.scalars(query).all())


@app.get("/metrics/{metric_date}", response_model=DailyMetricsRead)
def get_metric(metric_date: date, db: Session = Depends(get_db)) -> DailyMetrics:
    metric = db.scalar(select(DailyMetrics).where(DailyMetrics.metric_date == metric_date).limit(1))
    if not metric:
        raise HTTPException(status_code=404, detail="Metric for date not found")
    return metric
