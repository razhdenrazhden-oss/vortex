from dataclasses import dataclass


@dataclass
class HeartInput:
    avg_hr: float | None
    avg_hrv: float | None
    avg_tsb: float | None
    high_fatigue_days: int


def determine_cardio_risk(data: HeartInput) -> str:
    # High risk: low HRV + strong negative TSB and repeated high fatigue.
    if (data.avg_hrv is not None and data.avg_hrv < 40) and (
        data.avg_tsb is not None and data.avg_tsb <= -20
    ):
        return "High Risk"

    if data.high_fatigue_days >= 3 and (data.avg_tsb is not None and data.avg_tsb <= -15):
        return "High Risk"

    # Slight risk: elevated HR and high fatigue or moderate negative balance.
    if (data.avg_hr is not None and data.avg_hr > 68) and (
        data.high_fatigue_days >= 1 or (data.avg_tsb is not None and data.avg_tsb < -8)
    ):
        return "Slight Risk"

    if data.avg_hrv is not None and data.avg_hrv < 50:
        return "Slight Risk"

    return "Normal"


def heart_recommendations(risk_level: str) -> list[str]:
    if risk_level == "High Risk":
        return [
            "Recovery day / light ride",
            "Focus on sleep and hydration",
            "Consult physician if abnormal HR persists",
        ]
    if risk_level == "Slight Risk":
        return [
            "Light recovery ride today",
            "Focus on sleep and hydration",
        ]
    return [
        "Cardio markers are stable",
        "Proceed with planned endurance progression",
    ]
