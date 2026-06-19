"""
AcquiSight AI — Recommendation Engine
Size-tiered recommendations calibrated for PE / IB deal types.
"""

from __future__ import annotations

MEGA_CAP = 50_000_000_000
LARGE_CAP = 1_000_000_000
MID_MARKET = 100_000_000


def get_recommendation(
    revenue: float,
    investment_score: int,
    risk_score: int,
) -> tuple[str, str]:
    """
    Map company profile to a size-appropriate investment recommendation.

    Mega-cap (>$50B): Elite compounder vs not feasible for acquisition
    Large-cap ($1B–$50B): Strategic target
    Mid-market ($100M–$1B): PE platform
    Small-cap (<$100M): Growth equity / buyout candidate
    """
    if revenue > MEGA_CAP:
        if investment_score >= 70:
            return "Elite Public Market Compounder", "#22c55e"
        return "Strategic Acquisition Not Feasible", "#64748b"

    if revenue >= LARGE_CAP:
        if investment_score >= 65 and risk_score <= 50:
            return "Large-Cap Strategic Target", "#3b82f6"
        if investment_score >= 50:
            return "Large-Cap Strategic Target", "#6366f1"
        return "Strategic Acquisition Not Feasible", "#64748b"

    if revenue >= MID_MARKET:
        if investment_score >= 70 and risk_score <= 45:
            return "Attractive PE Platform Investment", "#22c55e"
        if investment_score >= 55:
            return "Attractive PE Platform Investment", "#3b82f6"
        if investment_score >= 40:
            return "Requires Further Due Diligence", "#eab308"
        return "High Risk Opportunity", "#f97316"

    # Sub-$100M
    if investment_score >= 75 and risk_score <= 40:
        return "Growth Equity / PE Buyout Candidate", "#22c55e"
    if investment_score >= 60:
        return "Growth Equity / PE Buyout Candidate", "#3b82f6"
    if investment_score >= 45:
        return "Requires Further Due Diligence", "#eab308"
    if investment_score >= 30:
        return "High Risk Opportunity", "#f97316"
    return "Reject", "#ef4444"
