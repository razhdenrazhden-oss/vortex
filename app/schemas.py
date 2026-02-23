from datetime import date, datetime

from pydantic import BaseModel, Field


class WorkoutCreate(BaseModel):
    workout_date: date
    tss: float = Field(gt=0, description="Training Stress Score")


class WorkoutRead(BaseModel):
    id: int
    workout_date: date
    tss: float
    created_at: datetime

    model_config = {"from_attributes": True}


class DailyMetricsRead(BaseModel):
    metric_date: date
    tss: float
    atl: float
    ctl: float
    tsb: float
    readiness_score: float

    model_config = {"from_attributes": True}
