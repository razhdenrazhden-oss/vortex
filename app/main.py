from datetime import date, timedelta
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.calculations import calculate_metrics
from app.database import SessionLocal, engine
from app.models import Base, Biometrics, DailyMetrics, DailyStatus, User, Workout
from app.schemas import (
    BiometricsCreate,
    BiometricsRead,
    DailyMetricsRead,
    DailyStatusRead,
    DashboardRead,
    UserCreate,
    UserRead,
    WorkoutCreate,
    WorkoutRead,
)

app = FastAPI(title="Activity Load Tracker API", version="0.5.0")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _iter_days(start: date, end: date) -> Generator[date, None, None]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _fatigue_level_from_tsb(tsb: float) -> str:
    if tsb <= -20:
        return "high"
    if tsb <= -5:
        return "moderate"
    return "low"


def _get_existing_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def recompute_metrics_from(db: Session, user_id: int, from_date: date) -> None:
    """
    Keep PR#2 behavior: continuous daily recomputation including rest days.
    Fully user-scoped for SaaS isolation.
    """
    latest_workout_date = db.scalar(select(func.max(Workout.workout_date)).where(Workout.user_id == user_id))
    if latest_workout_date is None:
        return

    prior_metric = db.scalar(
        select(DailyMetrics)
        .where(DailyMetrics.user_id == user_id, DailyMetrics.metric_date < from_date)
        .order_by(DailyMetrics.metric_date.desc())
        .limit(1)
    )
    prev_atl = prior_metric.atl if prior_metric else 0.0
    prev_ctl = prior_metric.ctl if prior_metric else 0.0

    day_tss_rows = db.execute(
        select(Workout.workout_date, func.sum(Workout.tss))
        .where(
            Workout.user_id == user_id,
            Workout.workout_date >= from_date,
            Workout.workout_date <= latest_workout_date,
        )
        .group_by(Workout.workout_date)
    ).all()
    day_tss_map = {row[0]: float(row[1]) for row in day_tss_rows}

    existing_metrics_by_date = {
        metric.metric_date: metric
        for metric in db.execute(
            select(DailyMetrics).where(
                DailyMetrics.user_id == user_id,
                DailyMetrics.metric_date >= from_date,
                DailyMetrics.metric_date <= latest_workout_date,
            )
        ).scalars()
    }
    existing_status_by_date = {
        status.status_date: status
        for status in db.execute(
            select(DailyStatus).where(
                DailyStatus.user_id == user_id,
                DailyStatus.status_date >= from_date,
                DailyStatus.status_date <= latest_workout_date,
            )
        ).scalars()
    }

    for metric_day in _iter_days(from_date, latest_workout_date):
        day_tss = day_tss_map.get(metric_day, 0.0)
        atl, ctl, tsb, readiness = calculate_metrics(prev_atl=prev_atl, prev_ctl=prev_ctl, today_tss=day_tss)
        fatigue_level = _fatigue_level_from_tsb(tsb)

        metric = existing_metrics_by_date.get(metric_day)
        if metric:
            metric.tss = day_tss
            metric.atl = atl
            metric.ctl = ctl
            metric.tsb = tsb
            metric.readiness_score = readiness
        else:
            db.add(
                DailyMetrics(
                    user_id=user_id,
                    metric_date=metric_day,
                    tss=day_tss,
                    atl=atl,
                    ctl=ctl,
                    tsb=tsb,
                    readiness_score=readiness,
                )
            )

        status = existing_status_by_date.get(metric_day)
        if status:
            status.readiness_score = readiness
            status.tsb = tsb
            status.fatigue_level = fatigue_level
        else:
            db.add(
                DailyStatus(
                    user_id=user_id,
                    status_date=metric_day,
                    readiness_score=readiness,
                    fatigue_level=fatigue_level,
                    tsb=tsb,
                )
            )

        prev_atl, prev_ctl = atl, ctl


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/users", response_model=UserRead, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    try:
        user = User(
            external_auth_id=payload.external_auth_id,
            subscription_tier=payload.subscription_tier,
            subscription_status=payload.subscription_status,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="User with external_auth_id already exists") from exc


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    return _get_existing_user(db, user_id)


@app.post("/workouts", response_model=WorkoutRead, status_code=201)
def create_workout(payload: WorkoutCreate, db: Session = Depends(get_db)) -> Workout:
    _get_existing_user(db, payload.user_id)
    try:
        workout = Workout(user_id=payload.user_id, workout_date=payload.workout_date, tss=payload.tss)
        db.add(workout)
        db.flush()
        recompute_metrics_from(db=db, user_id=payload.user_id, from_date=payload.workout_date)
        db.commit()
        db.refresh(workout)
        return workout
    except Exception:
        db.rollback()
        raise


@app.get("/workouts", response_model=list[WorkoutRead])
def list_workouts(
    user_id: int = Query(..., gt=0),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Workout]:
    if start and end and start > end:
        raise HTTPException(status_code=400, detail="start must be less than or equal to end")

    query = select(Workout).where(Workout.user_id == user_id)
    if start:
        query = query.where(Workout.workout_date >= start)
    if end:
        query = query.where(Workout.workout_date <= end)
    query = query.order_by(Workout.workout_date.asc(), Workout.created_at.asc())
    return list(db.scalars(query).all())


@app.get("/metrics", response_model=list[DailyMetricsRead])
def list_metrics(
    user_id: int = Query(..., gt=0),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[DailyMetrics]:
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be less than or equal to end_date")

    query = select(DailyMetrics).where(DailyMetrics.user_id == user_id)
    if start_date:
        query = query.where(DailyMetrics.metric_date >= start_date)
    if end_date:
        query = query.where(DailyMetrics.metric_date <= end_date)
    query = query.order_by(DailyMetrics.metric_date.asc())
    return list(db.scalars(query).all())


@app.get("/metrics/{metric_date}", response_model=DailyMetricsRead)
def get_metric(metric_date: date, user_id: int = Query(..., gt=0), db: Session = Depends(get_db)) -> DailyMetrics:
    metric = db.scalar(
        select(DailyMetrics)
        .where(DailyMetrics.user_id == user_id, DailyMetrics.metric_date == metric_date)
        .limit(1)
    )
    if not metric:
        raise HTTPException(status_code=404, detail="Metric for date not found")
    return metric


@app.get("/daily-status", response_model=list[DailyStatusRead])
def list_daily_status(
    user_id: int = Query(..., gt=0),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[DailyStatus]:
    if start and end and start > end:
        raise HTTPException(status_code=400, detail="start must be less than or equal to end")

    query = select(DailyStatus).where(DailyStatus.user_id == user_id)
    if start:
        query = query.where(DailyStatus.status_date >= start)
    if end:
        query = query.where(DailyStatus.status_date <= end)
    query = query.order_by(DailyStatus.status_date.asc())
    return list(db.scalars(query).all())


@app.get("/users/{user_id}/dashboard", response_model=DashboardRead)
def get_dashboard(user_id: int, db: Session = Depends(get_db)) -> DashboardRead:
    _get_existing_user(db, user_id)

    latest_metric = db.scalar(
        select(DailyMetrics)
        .where(DailyMetrics.user_id == user_id)
        .order_by(DailyMetrics.metric_date.desc())
        .limit(1)
    )
    latest_status = db.scalar(
        select(DailyStatus)
        .where(DailyStatus.user_id == user_id)
        .order_by(DailyStatus.status_date.desc())
        .limit(1)
    )
    last_workout = db.scalar(
        select(Workout)
        .where(Workout.user_id == user_id)
        .order_by(Workout.workout_date.desc(), Workout.created_at.desc())
        .limit(1)
    )
    latest_biometrics = db.scalar(
        select(Biometrics)
        .where(Biometrics.user_id == user_id)
        .order_by(Biometrics.entry_date.desc(), Biometrics.created_at.desc())
        .limit(1)
    )

    return DashboardRead(
        user_id=user_id,
        latest_metric=latest_metric,
        latest_status=latest_status,
        last_workout=last_workout,
        latest_biometrics=latest_biometrics,
    )


@app.post("/biometrics", response_model=BiometricsRead, status_code=201)
def create_biometrics(payload: BiometricsCreate, db: Session = Depends(get_db)) -> Biometrics:
    _get_existing_user(db, payload.user_id)
    try:
        biometrics = Biometrics(
            user_id=payload.user_id,
            entry_date=payload.entry_date,
            hr=payload.hr,
            lactate=payload.lactate,
            glucose=payload.glucose,
            steps=payload.steps,
        )
        db.add(biometrics)
        db.commit()
        db.refresh(biometrics)
        return biometrics
    except Exception:
        db.rollback()
        raise
