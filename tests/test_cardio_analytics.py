from app.cardio_analytics import CardioInput, cardio_recommendations, cardio_risk_level, compute_cardio_score


def test_cardio_score_bounds_with_extreme_values():
    high = compute_cardio_score(
        CardioInput(avg_readiness=100, avg_tsb=30, hr=45, lactate=1.2, glucose=90, steps=15000)
    )
    low = compute_cardio_score(
        CardioInput(avg_readiness=0, avg_tsb=-40, hr=80, lactate=5.5, glucose=180, steps=1000)
    )
    assert 0 <= high <= 100
    assert 0 <= low <= 100
    assert high > low


def test_cardio_risk_levels():
    assert cardio_risk_level(80) == "low"
    assert cardio_risk_level(60) == "moderate"
    assert cardio_risk_level(40) == "high"


def test_cardio_recommendations_present_for_risk_factors():
    data = CardioInput(avg_readiness=30, avg_tsb=-15, hr=72, lactate=3.1, glucose=130, steps=2500)
    score = compute_cardio_score(data)
    recs = cardio_recommendations(data, score)
    assert len(recs) >= 2
