from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


class WorkoutCreate(BaseModel):
    user_id: int = Field(gt=0)
    workout_date: date
    tss: float = Field(gt=0, description="Training Stress Score")


class WorkoutRead(BaseModel):
    id: int
    user_id: int
    workout_date: date
    tss: float
    created_at: datetime

    model_config = {"from_attributes": True}


class DailyMetricsRead(BaseModel):
    user_id: int
    metric_date: date
    tss: float
    atl: float
    ctl: float
    tsb: float
    readiness_score: float

    model_config = {"from_attributes": True}


class DailyStatusRead(BaseModel):
    user_id: int
    status_date: date
    readiness_score: float
    fatigue_level: str
    tsb: float

    model_config = {"from_attributes": True}


class BiometricsCreate(BaseModel):
    user_id: int = Field(gt=0)
    entry_date: date
    resting_hr: float | None = Field(default=None, gt=0)
    hrv: float | None = Field(default=None, gt=0)
    body_weight: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_any_metric_present(self) -> "BiometricsCreate":
        if self.resting_hr is None and self.hrv is None and self.body_weight is None:
            raise ValueError("At least one biometric field is required")
        return self


class BiometricsRead(BaseModel):
    id: int
    user_id: int
    entry_date: date
    resting_hr: float | None
    hrv: float | None
    body_weight: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardRead(BaseModel):
    user_id: int
    latest_metric: DailyMetricsRead | None
    latest_status: DailyStatusRead | None
    last_workout: WorkoutRead | None
