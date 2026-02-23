import os
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.activity_aggregation import classify_workout, normalize_units, recompute_form_points
from app.auth import AuthContext, get_current_user
from app.database import SessionLocal
from app.models import ExternalActivity, FormPoint, UserToken
from app.schemas import ActivityRead, FormPointRead, FormResponse, OAuthStartResponse, OAuthTokenInput

router = APIRouter(tags=["external-sync"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _upsert_activity(db: Session, activity: ExternalActivity) -> None:
    existing = (
        db.query(ExternalActivity)
        .filter(
            ExternalActivity.user_id == activity.user_id,
            ExternalActivity.source == activity.source,
            ExternalActivity.source_activity_id == activity.source_activity_id,
        )
        .first()
    )
    if existing:
        existing.activity_date = activity.activity_date
        existing.hr_bpm = activity.hr_bpm
        existing.power_w = activity.power_w
        existing.distance_km = activity.distance_km
        existing.duration_min = activity.duration_min
        existing.elevation_m = activity.elevation_m
        existing.workout_type = activity.workout_type
    else:
        db.add(activity)


def recompute_form_for_user(db: Session, user_id: int) -> None:
    start = date.today() - timedelta(days=365)
    end = date.today()

    rows = (
        db.query(ExternalActivity.activity_date, func.sum(ExternalActivity.distance_km * 2.0 + ExternalActivity.duration_min * 0.6))
        .filter(ExternalActivity.user_id == user_id, ExternalActivity.activity_date >= start)
        .group_by(ExternalActivity.activity_date)
        .all()
    )
    load_map = {r[0]: float(r[1]) for r in rows}
    points = recompute_form_points(load_map, start=start, end=end)

    db.query(FormPoint).filter(FormPoint.user_id == user_id, FormPoint.point_date >= start).delete()
    for p in points:
        db.add(
            FormPoint(
                user_id=user_id,
                point_date=p["date"],
                atl=p["atl"],
                ctl=p["ctl"],
                tsb=p["tsb"],
                load_state=p["load_state"],
            )
        )


@router.get("/auth/strava", response_model=OAuthStartResponse)
def auth_strava_start(auth: AuthContext = Depends(get_current_user)) -> OAuthStartResponse:
    client_id = os.getenv("STRAVA_CLIENT_ID", "demo-client-id")
    redirect_uri = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:8000/auth/strava/callback")
    scope = "activity:read_all"
    url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
    )
    return OAuthStartResponse(authorization_url=url)


@router.get("/auth/strava/callback")
async def auth_strava_callback(code: str, auth: AuthContext = Depends(get_current_user), db: Session = Depends(get_db)):
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": os.getenv("STRAVA_CLIENT_ID", ""),
        "client_secret": os.getenv("STRAVA_CLIENT_SECRET", ""),
        "code": code,
        "grant_type": "authorization_code",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(token_url, data=payload)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Strava OAuth exchange failed") from exc

    db.add(
        UserToken(
            user_id=auth.user.id,
            provider="strava",
            access_token=data.get("access_token", ""),
            refresh_token=data.get("refresh_token"),
            expires_at=datetime.utcfromtimestamp(data["expires_at"]) if data.get("expires_at") else None,
        )
    )
    db.commit()
    return {"status": "connected"}


@router.post("/auth/intervals")
def auth_intervals_token(
    payload: OAuthTokenInput,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.add(
        UserToken(
            user_id=auth.user.id,
            provider="intervals",
            access_token=payload.api_token,
            refresh_token=None,
            expires_at=None,
        )
    )
    db.commit()
    return {"status": "connected"}


@router.get("/user/activities", response_model=list[ActivityRead])
def list_user_activities(
    start_date: date = Query(default=date.today() - timedelta(days=30)),
    end_date: date = Query(default=date.today()),
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(ExternalActivity)
        .filter(
            ExternalActivity.user_id == auth.user.id,
            and_(ExternalActivity.activity_date >= start_date, ExternalActivity.activity_date <= end_date),
        )
        .order_by(ExternalActivity.activity_date.asc())
        .all()
    )
    return rows


@router.get("/user/form", response_model=FormResponse)
def get_user_form(auth: AuthContext = Depends(get_current_user), db: Session = Depends(get_db)):
    recompute_form_for_user(db, auth.user.id)
    db.commit()

    points = (
        db.query(FormPoint)
        .filter(FormPoint.user_id == auth.user.id)
        .order_by(FormPoint.point_date.asc())
        .all()
    )
    return FormResponse(
        user_id=auth.user.id,
        points=[
            FormPointRead(date=p.point_date, atl=p.atl, ctl=p.ctl, tsb=p.tsb, load_state=p.load_state)
            for p in points
        ],
    )


@router.post("/user/upload-gpx")
async def upload_gpx(
    file: UploadFile = File(...),
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".gpx"):
        raise HTTPException(status_code=400, detail="Expected GPX file")

    raw = await file.read()
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise HTTPException(status_code=400, detail="Invalid GPX XML") from exc

    ns = {"gpx": "http://www.topografix.com/GPX/1/1"}
    trkpts = root.findall(".//gpx:trkpt", ns)
    if len(trkpts) < 2:
        raise HTTPException(status_code=400, detail="GPX has insufficient points")

    # Skeleton approximation for MVP import.
    duration_min = max(20.0, len(trkpts) * 0.2)
    distance_km = max(1.0, len(trkpts) * 0.03)
    elevation_m = 0.0

    distance_km, duration_min = normalize_units(distance_km * 1000.0, duration_min * 60.0)
    workout_type = classify_workout(distance_km=distance_km, avg_power_w=None, duration_min=duration_min)

    activity = ExternalActivity(
        user_id=auth.user.id,
        source="gpx",
        source_activity_id=f"gpx-{datetime.utcnow().timestamp()}",
        activity_date=date.today(),
        hr_bpm=None,
        power_w=None,
        distance_km=distance_km,
        duration_min=duration_min,
        elevation_m=elevation_m,
        workout_type=workout_type,
    )
    _upsert_activity(db, activity)
    recompute_form_for_user(db, auth.user.id)
    db.commit()

    return {
        "status": "imported",
        "distance_km": distance_km,
        "duration_min": duration_min,
        "workout_type": workout_type,
        "source": "gpx",
    }
