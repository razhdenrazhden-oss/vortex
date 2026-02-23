from app.heart_analytics import HeartInput, determine_cardio_risk, heart_recommendations


def test_heart_risk_normal():
    risk = determine_cardio_risk(HeartInput(avg_hr=58, avg_hrv=62, avg_tsb=-2, high_fatigue_days=0))
    assert risk == "Normal"


def test_heart_risk_slight():
    risk = determine_cardio_risk(HeartInput(avg_hr=72, avg_hrv=52, avg_tsb=-10, high_fatigue_days=1))
    assert risk == "Slight Risk"


def test_heart_risk_high():
    risk = determine_cardio_risk(HeartInput(avg_hr=75, avg_hrv=35, avg_tsb=-25, high_fatigue_days=4))
    assert risk == "High Risk"


def test_heart_recommendations_for_high_risk_contains_medical_hint():
    recs = heart_recommendations("High Risk")
    assert any("Consult physician" in r for r in recs)
