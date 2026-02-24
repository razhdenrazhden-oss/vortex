from dataclasses import dataclass


@dataclass
class CardioInput:
    avg_readiness: float | None
    avg_tsb: float | None
    hr: float | None
    lactate: float | None
    glucose: float | None
    steps: float | None


def _bounded(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def compute_cardio_score(data: CardioInput) -> float:
    """
    Optional cardiovascular score [0..100].

    Uses readiness/TSB as recovery signal and biometrics as physiological context.
    Missing values are ignored (feature remains optional).
    """
    score = 50.0

    if data.avg_readiness is not None:
        score += (data.avg_readiness - 50.0) * 0.4

    if data.avg_tsb is not None:
        score += max(-10.0, min(10.0, data.avg_tsb * 0.5))

    if data.hr is not None:
        # Lower resting HR generally indicates better cardiovascular fitness.
        if data.hr <= 52:
            score += 8
        elif data.hr <= 60:
            score += 3
        elif data.hr >= 75:
            score -= 8
        elif data.hr >= 68:
            score -= 4

    if data.lactate is not None:
        if data.lactate > 4.0:
            score -= 8
        elif data.lactate > 2.5:
            score -= 4

    if data.glucose is not None:
        if data.glucose > 140:
            score -= 8
        elif data.glucose > 110:
            score -= 4
        elif data.glucose < 70:
            score -= 6

    if data.steps is not None:
        if data.steps >= 10000:
            score += 5
        elif data.steps < 4000:
            score -= 5

    return round(_bounded(score), 2)


def cardio_risk_level(score: float) -> str:
    if score >= 75:
        return "low"
    if score >= 50:
        return "moderate"
    return "high"


def cardio_recommendations(data: CardioInput, score: float) -> list[str]:
    recs: list[str] = []

    if score < 50:
        recs.append("Reduce intensity for 24-48h and prioritize recovery aerobic sessions.")

    if data.hr is not None and data.hr >= 68:
        recs.append("Elevated resting HR detected: prioritize sleep and hydration.")

    if data.lactate is not None and data.lactate > 2.5:
        recs.append("High lactate trend: include low-intensity base training and longer cooldowns.")

    if data.glucose is not None and data.glucose > 110:
        recs.append("Glucose above optimal range: review nutrition timing and carbohydrate load.")

    if data.steps is not None and data.steps < 4000:
        recs.append("Low daily movement: add 20-40 min easy walking.")

    if not recs:
        recs.append("Cardiovascular indicators are stable. Continue current progressive plan.")

    return recs
