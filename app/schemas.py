from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


class UserCreate(BaseModel):
    external_auth_id: str | None = Field(default=None, min_length=1, max_length=128)
    subscription_tier: str = Field(default="free", min_length=1, max_length=32)
    subscription_status: str = Field(default="active", min_length=1, max_length=32)


class UserRead(BaseModel):
    id: int
    external_auth_id: str | None
    subscription_tier: str
    subscription_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkoutCreate(BaseModel):
    user_id: int = Field(gt=0)
    workout_date: date
    tss: float = Field(gt=0, description="Training Stress Score")


class WorkoutUpdate(BaseModel):
    tss: float | None = Field(default=None, gt=0, description="Training Stress Score")
    workout_date: date | None = None

    @model_validator(mode="after")
    def validate_any_field_present(self) -> "WorkoutUpdate":
        if self.tss is None and self.workout_date is None:
            raise ValueError("At least one field must be provided")
        return self


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


class HeartStatusRead(BaseModel):
    user_id: int
    metric_date: date
    avg_hr: float | None
    avg_hrv: float | None
    cardio_risk_level: str
    recommendations: list[str]

    model_config = {"from_attributes": True}


class BiometricsCreate(BaseModel):
    user_id: int = Field(gt=0)
    entry_date: date
    hr: float | None = Field(default=None, gt=0)
    hrv: float | None = Field(default=None, gt=0)
    lactate: float | None = Field(default=None, gt=0)
    glucose: float | None = Field(default=None, gt=0)
    steps: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_any_metric_present(self) -> "BiometricsCreate":
        if self.hr is None and self.hrv is None and self.lactate is None and self.glucose is None and self.steps is None:
            raise ValueError("At least one biometric field is required")
        return self


class BiometricsRead(BaseModel):
    id: int
    user_id: int
    entry_date: date
    hr: float | None
    hrv: float | None
    lactate: float | None
    glucose: float | None
    steps: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardRead(BaseModel):
    user_id: int
    latest_metric: DailyMetricsRead | None
    latest_status: DailyStatusRead | None
    latest_heart_status: HeartStatusRead | None
    last_workout: WorkoutRead | None
    latest_biometrics: BiometricsRead | None


class CardioAnalyticsRead(BaseModel):
    user_id: int
    period_days: int
    cardio_score: float
    risk_level: str
    avg_readiness: float | None
    avg_tsb: float | None
    latest_hr: float | None
    latest_lactate: float | None
    latest_glucose: float | None
    latest_steps: float | None
    recommendations: list[str]




class RouteInfo(BaseModel):
    url: str | None
    polyline: str | None


class ActivityRead(BaseModel):
    date: date
    source: str
    hr_bpm: float | None
    power_w: float | None
    distance_km: float
    duration_min: float
    elevation_m: float | None
    workout_type: str | None
    atl: float | None
    ctl: float | None
    tsb: float | None
    color: str | None
    route: RouteInfo



class FormPointRead(BaseModel):
    date: date
    atl: float
    ctl: float
    tsb: float
    load_state: str
    load_color: str


class FormResponse(BaseModel):
    user_id: int
    points: list[FormPointRead]


class OAuthStartResponse(BaseModel):
    authorization_url: str


class OAuthTokenInput(BaseModel):
    api_token: str = Field(min_length=8)
