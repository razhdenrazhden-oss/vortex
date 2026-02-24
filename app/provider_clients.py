from __future__ import annotations

from datetime import date

import httpx


class ProviderUnavailableError(Exception):
    pass


async def fetch_strava_activities(access_token: str, start: date, end: date) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://www.strava.com/api/v3/athlete/activities",
                params={"after": int(start.strftime("%s")), "before": int(end.strftime("%s"))},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            raw = resp.json()
    except Exception as exc:
        raise ProviderUnavailableError("Strava API unavailable") from exc

    return [
        {
            "source": "strava",
            "source_activity_id": str(item.get("id")),
            "activity_date": item.get("start_date_local", "")[:10],
            "hr_bpm": item.get("average_heartrate"),
            "power_w": item.get("average_watts"),
            "distance_m": item.get("distance", 0),
            "duration_s": item.get("moving_time", 0),
            "elevation_m": item.get("total_elevation_gain"),
            "route_url": f"https://www.strava.com/activities/{item.get('id')}" if item.get("id") else None,
            "polyline": ((item.get("map") or {}).get("summary_polyline")),
        }
        for item in raw
    ]


async def fetch_intervals_activities(api_token: str, start: date, end: date) -> list[dict]:
    # Skeleton endpoint shape; adapt URL/fields in real integration.
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://intervals.icu/api/v1/athlete/activities",
                params={"start": start.isoformat(), "end": end.isoformat()},
                headers={"Authorization": f"Bearer {api_token}"},
            )
            resp.raise_for_status()
            raw = resp.json()
    except Exception as exc:
        raise ProviderUnavailableError("Intervals.icu API unavailable") from exc

    return [
        {
            "source": "intervals",
            "source_activity_id": str(item.get("id")),
            "activity_date": item.get("start_date", "")[:10],
            "hr_bpm": item.get("avg_hr"),
            "power_w": item.get("avg_power"),
            "distance_m": (item.get("distance_km") or 0) * 1000.0,
            "duration_s": (item.get("duration_min") or 0) * 60.0,
            "elevation_m": item.get("elevation_m"),
            "route_url": item.get("activity_url"),
            "polyline": item.get("polyline"),
        }
        for item in raw
    ]


async def fetch_komoot_activities(access_token: str, start: date, end: date) -> list[dict]:
    # Komoot API access depends on partner account; keep optional skeleton.
    _ = (access_token, start, end)
    return []


async def fetch_garmin_activities(access_token: str, start: date, end: date) -> list[dict]:
    # Garmin Connect does not provide open public API for all apps; optional skeleton.
    _ = (access_token, start, end)
    return []
