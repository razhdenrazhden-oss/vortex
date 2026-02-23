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


def _create_user(client: TestClient, external_auth_id: str = "auth_1") -> int:
    resp = client.post("/users", json={"external_auth_id": external_auth_id})
    assert resp.status_code == 201
    return resp.json()["id"]


def test_post_workout_requires_existing_user_and_creates_daily_status(client: TestClient):
    missing_user = client.post("/workouts", json={"user_id": 999, "workout_date": "2026-01-01", "tss": 80})
    assert missing_user.status_code == 404

    user_id = _create_user(client, "auth_user_w")
    response = client.post("/workouts", json={"user_id": user_id, "workout_date": "2026-01-01", "tss": 80})
    assert response.status_code == 201
    assert response.json()["user_id"] == user_id

    status_resp = client.get("/daily-status", params={"user_id": user_id})
    assert status_resp.status_code == 200
    payload = status_resp.json()
    assert len(payload) == 1
    assert payload[0]["status_date"] == "2026-01-01"


def test_metrics_endpoint_start_end_and_edge_equal_dates(client: TestClient):
    user_id = _create_user(client, "auth_metrics")
    client.post("/workouts", json={"user_id": user_id, "workout_date": "2026-01-01", "tss": 100})
    client.post("/workouts", json={"user_id": user_id, "workout_date": "2026-01-10", "tss": 50})

    single_day = client.get(
        "/metrics",
        params={"user_id": user_id, "start_date": "2026-01-10", "end_date": "2026-01-10"},
    )
    assert single_day.status_code == 200
    assert len(single_day.json()) == 1

    invalid_range = client.get(
        "/metrics",
        params={"user_id": user_id, "start_date": "2026-01-11", "end_date": "2026-01-10"},
    )
    assert invalid_range.status_code == 400


def test_metrics_no_workouts_large_gaps_and_user_isolation(client: TestClient):
    user_a = _create_user(client, "auth_a")
    user_b = _create_user(client, "auth_b")

    empty = client.get("/metrics", params={"user_id": user_a})
    assert empty.status_code == 200
    assert empty.json() == []

    client.post("/workouts", json={"user_id": user_a, "workout_date": "2026-01-01", "tss": 40})
    client.post("/workouts", json={"user_id": user_a, "workout_date": "2026-02-01", "tss": 60})
    client.post("/workouts", json={"user_id": user_b, "workout_date": "2026-01-15", "tss": 120})

    gap_window = client.get(
        "/metrics",
        params={"user_id": user_a, "start_date": "2026-01-01", "end_date": "2026-02-01"},
    )
    assert gap_window.status_code == 200
    assert len(gap_window.json()) == 32

    isolated = client.get("/metrics", params={"user_id": user_b})
    assert isolated.status_code == 200
    assert len(isolated.json()) == 1


def test_dashboard_workouts_and_biometrics_endpoints(client: TestClient):
    user_id = _create_user(client, "auth_dash")

    w1 = client.post("/workouts", json={"user_id": user_id, "workout_date": "2026-01-03", "tss": 70})
    assert w1.status_code == 201

    wr = client.get("/workouts", params={"user_id": user_id, "start": "2026-01-01", "end": "2026-01-31"})
    assert wr.status_code == 200
    assert len(wr.json()) == 1

    b = client.post(
        "/biometrics",
        json={"user_id": user_id, "entry_date": "2026-01-03", "hr": 50, "glucose": 92, "steps": 11000},
    )
    assert b.status_code == 201

    dashboard = client.get(f"/users/{user_id}/dashboard")
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["latest_status"] is not None
    assert body["latest_biometrics"] is not None
