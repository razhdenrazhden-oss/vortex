from datetime import datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    workout_date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    tss: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class DailyMetrics(Base):
    __tablename__ = "daily_metrics"
    __table_args__ = (UniqueConstraint("user_id", "metric_date", name="uq_daily_metrics_user_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    metric_date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    tss: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    atl: Mapped[float] = mapped_column(Float, nullable=False)
    ctl: Mapped[float] = mapped_column(Float, nullable=False)
    tsb: Mapped[float] = mapped_column(Float, nullable=False)
    readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class DailyStatus(Base):
    __tablename__ = "daily_status"
    __table_args__ = (UniqueConstraint("user_id", "status_date", name="uq_daily_status_user_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    status_date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    fatigue_level: Mapped[str] = mapped_column(String(32), nullable=False)
    tsb: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class Biometrics(Base):
    __tablename__ = "biometrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    entry_date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    resting_hr: Mapped[float | None] = mapped_column(Float, nullable=True)
    hrv: Mapped[float | None] = mapped_column(Float, nullable=True)
    body_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
