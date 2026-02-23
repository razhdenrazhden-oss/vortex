from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.models import Base


@pytest.fixture()
def client():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_post_workout_and_daily_status_created(client: TestClient):
    response = client.post("/workouts", json={"user_id": 1, "workout_date": "2026-01-01", "tss": 80})
    assert response.status_code == 201
    assert response.json()["user_id"] == 1

    status_resp = client.get("/daily-status", params={"user_id": 1})
    assert status_resp.status_code == 200
    payload = status_resp.json()
    assert len(payload) == 1
    assert payload[0]["status_date"] == "2026-01-01"
    assert payload[0]["fatigue_level"] in {"low", "moderate", "high"}


def test_metrics_endpoint_start_end_and_edge_equal_dates(client: TestClient):
    client.post("/workouts", json={"user_id": 1, "workout_date": "2026-01-01", "tss": 100})
    client.post("/workouts", json={"user_id": 1, "workout_date": "2026-01-10", "tss": 50})

    single_day = client.get(
        "/metrics",
        params={"user_id": 1, "start_date": "2026-01-10", "end_date": "2026-01-10"},
    )
    assert single_day.status_code == 200
    items = single_day.json()
    assert len(items) == 1
    assert items[0]["metric_date"] == "2026-01-10"

    invalid_range = client.get(
        "/metrics",
        params={"user_id": 1, "start_date": "2026-01-11", "end_date": "2026-01-10"},
    )
    assert invalid_range.status_code == 400


def test_metrics_no_workouts_and_large_gaps(client: TestClient):
    empty = client.get("/metrics", params={"user_id": 999})
    assert empty.status_code == 200
    assert empty.json() == []

    client.post("/workouts", json={"user_id": 2, "workout_date": "2026-01-01", "tss": 40})
    client.post("/workouts", json={"user_id": 2, "workout_date": "2026-02-01", "tss": 60})

    gap_window = client.get(
        "/metrics",
        params={"user_id": 2, "start_date": "2026-01-01", "end_date": "2026-02-01"},
    )
    assert gap_window.status_code == 200
    data = gap_window.json()
    assert data[0]["metric_date"] == "2026-01-01"
    assert data[-1]["metric_date"] == "2026-02-01"
    assert len(data) == 32


def test_dashboard_workouts_and_biometrics_endpoints(client: TestClient):
    w1 = client.post("/workouts", json={"user_id": 3, "workout_date": "2026-01-03", "tss": 70})
    assert w1.status_code == 201

    wr = client.get("/workouts", params={"user_id": 3, "start": "2026-01-01", "end": "2026-01-31"})
    assert wr.status_code == 200
    assert len(wr.json()) == 1

    b = client.post(
        "/biometrics",
        json={"user_id": 3, "entry_date": "2026-01-03", "resting_hr": 50, "hrv": 70},
    )
    assert b.status_code == 201

    dashboard = client.get("/users/3/dashboard")
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["user_id"] == 3
    assert body["latest_status"] is not None
    assert body["last_workout"] is not None
