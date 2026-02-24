def next_load(previous_value: float, input_tss: float, tau_days: float) -> float:
    """Exponential moving average load update."""
    return previous_value + (input_tss - previous_value) * (1.0 / tau_days)


def calculate_metrics(prev_atl: float, prev_ctl: float, today_tss: float) -> tuple[float, float, float, float]:
    """
    Calculate ATL/CTL/TSB and normalized readiness score.

    Constants:
    - ATL time constant: 7 days
    - CTL time constant: 42 days
    """
    atl = next_load(prev_atl, today_tss, tau_days=7)
    ctl = next_load(prev_ctl, today_tss, tau_days=42)
    tsb = ctl - atl

    # Simple bounded normalization around fresh/fatigued ranges.
    # tsb <= -30 => 0, tsb >= +30 => 100
    readiness = max(0.0, min(100.0, 50.0 + (tsb / 30.0) * 50.0))
    return atl, ctl, tsb, readiness
