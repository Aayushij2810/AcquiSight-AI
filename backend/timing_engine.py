"""
AcquiSight AI — Investment Timing Engine

Analytical assessment of whether current fundamentals, valuation, growth,
and risk factors suggest a favorable or unfavorable investment window.

NOT financial advice. Outputs are framed as institutional-style research.
"""

from __future__ import annotations

from models import (
    CompsResult,
    DimensionScores,
    QuarterAttractiveness,
    TimingAnalysis,
    TimingCatalyst,
)

# ── INDUSTRY SEASONAL PROFILES ───────────────────────────────────────────────
# Base quarter multipliers (applied to timing sub-score). Higher = more attractive.

INDUSTRY_QUARTER_PROFILES: dict[str, dict[str, float]] = {
    "Technology": {"Q1": 0.78, "Q2": 0.88, "Q3": 0.82, "Q4": 0.95},
    "SaaS": {"Q1": 0.80, "Q2": 0.90, "Q3": 0.85, "Q4": 0.96},
    "Cybersecurity": {"Q1": 0.82, "Q2": 0.88, "Q3": 0.86, "Q4": 0.94},
    "Healthcare": {"Q1": 0.92, "Q2": 0.85, "Q3": 0.80, "Q4": 0.88},
    "Pharmaceuticals & Biotech": {"Q1": 0.88, "Q2": 0.82, "Q3": 0.78, "Q4": 0.90},
    "Consumer": {"Q1": 0.70, "Q2": 0.82, "Q3": 0.85, "Q4": 0.98},
    "Retail": {"Q1": 0.72, "Q2": 0.80, "Q3": 0.84, "Q4": 0.97},
    "E-Commerce": {"Q1": 0.75, "Q2": 0.83, "Q3": 0.86, "Q4": 0.96},
    "Fintech": {"Q1": 0.84, "Q2": 0.88, "Q3": 0.82, "Q4": 0.90},
    "Financial Services": {"Q1": 0.86, "Q2": 0.90, "Q3": 0.84, "Q4": 0.92},
    "Insurance": {"Q1": 0.85, "Q2": 0.88, "Q3": 0.83, "Q4": 0.89},
    "Energy": {"Q1": 0.88, "Q2": 0.92, "Q3": 0.86, "Q4": 0.84},
    "Manufacturing": {"Q1": 0.82, "Q2": 0.90, "Q3": 0.88, "Q4": 0.85},
    "default": {"Q1": 0.82, "Q2": 0.88, "Q3": 0.84, "Q4": 0.90},
}

INDUSTRY_TIMING_FACTORS: dict[str, list[str]] = {
    "Technology": [
        "Cloud spending cycles", "Enterprise budget cycles", "AI adoption trends",
        "Software renewal cycles", "Product launch timing",
    ],
    "SaaS": [
        "Cloud spending cycles", "Enterprise budget cycles", "AI adoption trends",
        "Software renewal cycles", "Product launch timing",
    ],
    "Cybersecurity": [
        "Enterprise security budget cycles", "Threat landscape intensity",
        "Compliance deadline clustering", "Annual contract renewals",
    ],
    "Healthcare": [
        "Hospital budget allocations", "Regulatory milestones", "Drug approval cycles",
        "Payer reimbursement cycles", "Seasonal procedure volumes",
    ],
    "Pharmaceuticals & Biotech": [
        "FDA approval timelines", "Clinical trial readouts", "Patent cliff exposure",
        "Hospital formulary cycles", "R&D budget allocations",
    ],
    "Consumer": [
        "Holiday demand seasonality", "Consumer confidence trends",
        "Inflation sensitivity", "Back-to-school / seasonal peaks",
    ],
    "Retail": [
        "Holiday demand seasonality", "Inventory build cycles",
        "Consumer confidence", "Promotional calendar timing",
    ],
    "Fintech": [
        "Interest rate environment", "Capital markets activity",
        "Credit conditions", "Loan demand cycles",
    ],
    "Insurance": [
        "Interest rate environment", "Underwriting cycle timing",
        "Catastrophe season exposure", "Regulatory capital requirements",
    ],
    "Financial Services": [
        "Interest rate environment", "Capital markets activity",
        "Credit conditions", "Loan demand",
    ],
}


def _timing_label(score: int) -> str:
    if score <= 20:
        return "Very Unattractive"
    if score <= 40:
        return "Unattractive"
    if score <= 60:
        return "Neutral"
    if score <= 80:
        return "Attractive"
    return "Highly Attractive"


def _outlook_label(score: int) -> str:
    if score >= 85:
        return "Highly Attractive"
    if score >= 70:
        return "Attractive"
    if score >= 50:
        return "Neutral"
    if score >= 30:
        return "Unattractive"
    return "Very Unattractive"


def _entry_window_label(score: int) -> str:
    if score >= 75:
        return "Favorable Entry Window"
    if score >= 55:
        return "Moderately Favorable Entry Window"
    if score >= 40:
        return "Neutral Entry Window"
    if score >= 25:
        return "Cautious Entry Window"
    return "Unfavorable Entry Window"


def _peer_avg_growth(comps: CompsResult) -> float:
    rates = [c.revenue_growth for c in comps.companies if c.revenue_growth is not None]
    return sum(rates) / len(rates) if rates else 10.0


def _peer_avg_margin(comps: CompsResult) -> float:
    margins = [c.ebitda_margin for c in comps.companies if c.ebitda_margin is not None]
    return sum(margins) / len(margins) if margins else 20.0


def _implied_ev_multiple(enterprise_value: float, ebitda: float) -> float:
    if ebitda <= 0:
        return 99.0
    return enterprise_value / ebitda


def _growth_stability_score(growth_rate: float, revenue: float) -> float:
    """Proxy for historical growth stability using scale and growth band."""
    if growth_rate < 0:
        return 25.0
    if revenue >= 10_000_000_000:
        base = 75.0
    elif revenue >= 1_000_000_000:
        base = 65.0
    elif revenue >= 100_000_000:
        base = 55.0
    else:
        base = 45.0
    if 8 <= growth_rate <= 25:
        base += 15
    elif 5 <= growth_rate < 8 or 25 < growth_rate <= 35:
        base += 8
    return min(100, base)


def _compute_confidence(
    revenue: float,
    ebitda: float,
    debt_to_ebitda: float | None,
    investment_score: int,
    risk_score: int,
    has_market_cap: bool,
) -> tuple[str, float]:
    points = 0.0
    if revenue > 0 and ebitda != 0:
        points += 25
    if debt_to_ebitda is not None:
        points += 20
    if investment_score > 0:
        points += 20
    if risk_score >= 0:
        points += 15
    if has_market_cap:
        points += 10
    if revenue >= 100_000_000:
        points += 10

    if points >= 85:
        return "Very High", points
    if points >= 70:
        return "High", points
    if points >= 50:
        return "Medium", points
    return "Low", points


def _build_quarters(base_timing: int, industry: str) -> list[QuarterAttractiveness]:
    profile = INDUSTRY_QUARTER_PROFILES.get(
        industry, INDUSTRY_QUARTER_PROFILES["default"]
    )
    quarters = []
    for q in ("Q1", "Q2", "Q3", "Q4"):
        raw = base_timing * profile[q]
        score = min(100, int(round(raw)))
        quarters.append(QuarterAttractiveness(
            quarter=q,
            attractiveness_score=score,
            outlook=_outlook_label(score),
        ))
    return quarters


def _build_catalysts(
    industry: str,
    growth_rate: float,
    ebitda_margin: float,
    peer_growth: float,
    peer_margin: float,
    investment_score: int,
) -> tuple[list[TimingCatalyst], list[TimingCatalyst]]:
    positive: list[TimingCatalyst] = []
    negative: list[TimingCatalyst] = []

    if growth_rate > peer_growth:
        positive.append(TimingCatalyst(
            category="Growth",
            name="Above-Peer Revenue Growth",
            description=f"Revenue growth of {growth_rate:.1f}% exceeds peer average of {peer_growth:.1f}%.",
        ))
    if ebitda_margin > peer_margin:
        positive.append(TimingCatalyst(
            category="Profitability",
            name="Margin Expansion vs Peers",
            description=f"EBITDA margin of {ebitda_margin:.1f}% above peer median of {peer_margin:.1f}%.",
        ))
    if investment_score >= 75:
        positive.append(TimingCatalyst(
            category="Fundamentals",
            name="Strong Investment Profile",
            description="Composite investment score supports favorable fundamental backdrop.",
        ))

    industry_key = industry
    if industry in ("Technology", "SaaS", "Cybersecurity"):
        positive.append(TimingCatalyst(
            category="Industry",
            name="AI Monetization & Cloud Tailwinds",
            description="Enterprise AI adoption and cloud spending cycles may support demand.",
        ))
        negative.append(TimingCatalyst(
            category="Industry",
            name="Competitive & Regulatory Pressure",
            description="Intensifying competition and regulatory scrutiny remain sector headwinds.",
        ))
    elif industry in ("Healthcare", "Pharmaceuticals & Biotech"):
        positive.append(TimingCatalyst(
            category="Industry",
            name="Healthcare Spending Resilience",
            description="Structural demand for healthcare services supports revenue durability.",
        ))
        negative.append(TimingCatalyst(
            category="Regulatory",
            name="Regulatory & Reimbursement Risk",
            description="Policy changes and approval timelines create execution uncertainty.",
        ))
    elif industry in ("Consumer", "Retail", "E-Commerce"):
        positive.append(TimingCatalyst(
            category="Seasonality",
            name="Peak Demand Windows",
            description="Holiday and seasonal demand cycles may create timing opportunities.",
        ))
        negative.append(TimingCatalyst(
            category="Macro",
            name="Consumer Confidence & Inflation Sensitivity",
            description="Spending patterns remain sensitive to macro conditions.",
        ))
    elif industry in ("Fintech", "Insurance", "Financial Services"):
        positive.append(TimingCatalyst(
            category="Macro",
            name="Capital Markets Activity",
            description="Favorable credit and rate environments may support sector multiples.",
        ))
        negative.append(TimingCatalyst(
            category="Macro",
            name="Rate & Credit Cycle Risk",
            description="Interest rate shifts and credit tightening pose sector headwinds.",
        ))
    else:
        positive.append(TimingCatalyst(
            category="Industry",
            name="Industry Tailwinds",
            description=f"Sector-specific demand drivers for {industry} remain supportive.",
        ))
        negative.append(TimingCatalyst(
            category="Execution",
            name="Execution & Cyclicality Risk",
            description="Operational execution and cyclical demand remain key variables.",
        ))

    if growth_rate >= 15:
        positive.append(TimingCatalyst(
            category="Growth",
            name="Strong Growth Trajectory",
            description="Elevated growth rate supports positive momentum assessment.",
        ))
    if ebitda_margin >= 25:
        positive.append(TimingCatalyst(
            category="Profitability",
            name="Operating Leverage Potential",
            description="Healthy margins suggest room for operating leverage improvements.",
        ))

    negative.append(TimingCatalyst(
        category="Valuation",
        name="Sector Multiple Compression Risk",
        description="Peer multiple volatility may affect relative valuation attractiveness.",
    ))
    negative.append(TimingCatalyst(
        category="Macro",
        name="Economic Slowdown Exposure",
        description="Broad macro deceleration could pressure growth and margins.",
    ))

    return positive[:6], negative[:6]


def _build_entry_reasons(
    growth_rate: float,
    peer_growth: float,
    ebitda_margin: float,
    peer_margin: float,
    debt_to_ebitda: float | None,
    risk_score: int,
    implied_multiple: float,
    peer_multiple: float,
) -> list[str]:
    reasons = []
    if growth_rate >= peer_growth:
        reasons.append("Revenue growth remains at or above peer average.")
    else:
        reasons.append("Revenue growth trails peer average — timing sensitivity elevated.")

    if ebitda_margin >= peer_margin:
        reasons.append("Margins remain competitive relative to peer group.")
    else:
        reasons.append("Margin profile below peers — monitor profitability trends.")

    if debt_to_ebitda is not None and debt_to_ebitda < 3:
        reasons.append("Balance sheet leverage remains manageable.")
    elif debt_to_ebitda is not None:
        reasons.append("Elevated leverage warrants cautious entry timing.")

    if risk_score <= 35:
        reasons.append("Risk profile remains relatively stable.")
    else:
        reasons.append("Risk score suggests elevated uncertainty in current window.")

    if implied_multiple <= peer_multiple * 1.1:
        reasons.append("Valuation appears reasonable relative to peer multiples.")
    else:
        reasons.append("Valuation trades at a premium to peer averages.")

    return reasons


def _build_narrative(
    company_name: str,
    timing_score: int,
    status: str,
    best_quarter: str,
    industry: str,
    positive: list[TimingCatalyst],
    negative: list[TimingCatalyst],
    confidence: str,
) -> str:
    pos_names = ", ".join(c.name.lower() for c in positive[:3])
    neg_names = ", ".join(c.name.lower() for c in negative[:2])
    factors = INDUSTRY_TIMING_FACTORS.get(industry, INDUSTRY_TIMING_FACTORS.get("Technology", []))
    factor_str = ", ".join(factors[:3]).lower() if factors else "sector-specific demand drivers"

    return (
        f"{company_name} currently scores {timing_score}/100 on the Investment Timing Engine "
        f"({status}). This analytical assessment — not investment advice — evaluates whether "
        f"current fundamentals, valuation levels, and sector trends suggest a "
        f"{status.lower()} window. {best_quarter} appears most attractive based on "
        f"{factor_str}. Primary catalysts include {pos_names}. "
        f"Key headwinds include {neg_names}. Confidence level: {confidence}."
    )


def compute_timing_analysis(
    company_name: str,
    industry: str,
    revenue: float,
    ebitda: float,
    growth_rate: float,
    ebitda_margin: float,
    debt_to_ebitda: float | None,
    enterprise_value: float,
    investment_score: int,
    risk_score: int,
    scores: DimensionScores,
    comps: CompsResult,
    market_cap: float | None = None,
) -> TimingAnalysis:
    """
    Generate full investment timing assessment.

    Analytical assessment based on company fundamentals, valuation metrics,
    and sector trends. Not financial advice.
    """
    peer_growth = _peer_avg_growth(comps)
    peer_margin = _peer_avg_margin(comps)
    peer_multiple = comps.base_multiple
    implied_multiple = _implied_ev_multiple(enterprise_value, ebitda)

    # Sub-scores (0–100, higher = more attractive timing)
    growth_vs_peer = min(100, max(20, 50 + (growth_rate - peer_growth) * 3))
    margin_vs_peer = min(100, max(20, 50 + (ebitda_margin - peer_margin) * 2))
    financial_health = scores.financial_health
    leverage_score = min(100, max(10, 100 - (debt_to_ebitda or 0) * 12)) if debt_to_ebitda is not None else 50
    valuation_score = min(100, max(15, 100 - max(0, implied_multiple - peer_multiple) * 4))
    risk_inverse = max(0, 100 - risk_score)
    stability = _growth_stability_score(growth_rate, revenue)
    investment_component = investment_score

    timing_score = int(round(
        growth_vs_peer * 0.15
        + margin_vs_peer * 0.10
        + financial_health * 0.10
        + leverage_score * 0.10
        + valuation_score * 0.12
        + risk_inverse * 0.15
        + stability * 0.08
        + investment_component * 0.20
    ))
    timing_score = min(100, max(0, timing_score))

    status = _timing_label(timing_score)
    entry_label = _entry_window_label(timing_score)
    quarters = _build_quarters(timing_score, industry)
    best_q = max(quarters, key=lambda q: q.attractiveness_score)

    confidence, confidence_numeric = _compute_confidence(
        revenue, ebitda, debt_to_ebitda, investment_score, risk_score, market_cap is not None
    )

    positive, negative = _build_catalysts(
        industry, growth_rate, ebitda_margin, peer_growth, peer_margin, investment_score
    )

    entry_reasons = _build_entry_reasons(
        growth_rate, peer_growth, ebitda_margin, peer_margin,
        debt_to_ebitda, risk_score, implied_multiple, peer_multiple,
    )

    narrative = _build_narrative(
        company_name, timing_score, status, best_q.quarter,
        industry, positive, negative, confidence,
    )

    industry_factors = INDUSTRY_TIMING_FACTORS.get(
        industry,
        ["Sector demand cycles", "Competitive dynamics", "Macro sensitivity"],
    )

    return TimingAnalysis(
        timing_score=timing_score,
        status=status,
        entry_window_assessment=entry_label,
        entry_window_reasons=entry_reasons,
        quarter_analysis=quarters,
        best_quarter=best_q.quarter,
        positive_catalysts=positive,
        risk_catalysts=negative,
        confidence_level=confidence,
        confidence_score=round(confidence_numeric, 1),
        analyst_commentary=narrative,
        industry_timing_factors=industry_factors,
        disclaimer=(
            "Analytical assessment based on company fundamentals, valuation metrics, "
            "and sector trends. Not financial advice. Does not constitute a recommendation "
            "to buy, sell, or hold any security."
        ),
        score_components={
            "growth_vs_peers": round(growth_vs_peer, 1),
            "margin_vs_peers": round(margin_vs_peer, 1),
            "financial_health": financial_health,
            "leverage": round(leverage_score, 1),
            "valuation_vs_peers": round(valuation_score, 1),
            "risk_adjusted": round(risk_inverse, 1),
            "growth_stability": round(stability, 1),
            "investment_score": investment_component,
        },
    )
