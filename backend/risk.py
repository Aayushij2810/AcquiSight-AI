"""
AcquiSight AI — Risk Scoring Engine
Computes a composite risk score (0–100, higher = riskier).
Imported by routers/screen.py via:
  from risk import compute_risk_score
"""


# ── HIGH-RISK JURISDICTION LISTS ──────────────────────────────────────────────
HIGH_RISK_COUNTRIES = {
    "Russia", "Venezuela", "Iran", "North Korea", "Belarus",
    "Myanmar", "Sudan", "Syria", "Libya", "Yemen",
}
MEDIUM_RISK_COUNTRIES = {
    "Argentina", "Turkey", "Pakistan", "Nigeria", "Egypt",
    "Ukraine", "Ethiopia", "Bangladesh", "Iraq", "Lebanon",
}


def _leverage_risk(debt_to_ebitda: float) -> float:
    """
    Leverage risk sub-score (0–100). High debt = high risk.
    >7x   → 100
    5–7x  → 70–100
    3–5x  → 40–70
    2–3x  → 20–40
    1–2x  → 5–20
    <1x   → 0–5
    """
    if debt_to_ebitda >= 7:
        return 100.0
    elif debt_to_ebitda >= 5:
        return 70 + ((debt_to_ebitda - 5) / 2) * 30
    elif debt_to_ebitda >= 3:
        return 40 + ((debt_to_ebitda - 3) / 2) * 30
    elif debt_to_ebitda >= 2:
        return 20 + ((debt_to_ebitda - 2) / 1) * 20
    elif debt_to_ebitda >= 1:
        return 5 + ((debt_to_ebitda - 1) / 1) * 15
    else:
        return max(0, debt_to_ebitda * 5)


def _margin_risk(ebitda_margin: float) -> float:
    """
    Margin risk sub-score (0–100). Thin margins = fragile operations.
    <0%   → 100
    0–5%  → 70–100
    5–15% → 40–70
    15–25%→ 15–40
    >25%  → 0–15
    """
    if ebitda_margin < 0:
        return 100.0
    elif ebitda_margin < 5:
        return 70 + ((5 - ebitda_margin) / 5) * 30
    elif ebitda_margin < 15:
        return 40 + ((15 - ebitda_margin) / 10) * 30
    elif ebitda_margin < 25:
        return 15 + ((25 - ebitda_margin) / 10) * 25
    else:
        return max(0, 15 - (ebitda_margin - 25) * 0.5)


def _growth_risk(growth_rate: float) -> float:
    """
    Growth risk sub-score (0–100). Decline or stagnation = elevated risk.
    <-10% → 100
    -10–0%→ 70–100
    0–5%  → 40–70
    5–15% → 10–40
    >15%  → 0–10
    """
    if growth_rate < -10:
        return 100.0
    elif growth_rate < 0:
        return 70 + ((0 - growth_rate) / 10) * 30
    elif growth_rate < 5:
        return 40 + ((5 - growth_rate) / 5) * 30
    elif growth_rate < 15:
        return 10 + ((15 - growth_rate) / 10) * 30
    else:
        return max(0, 10 - (growth_rate - 15) * 0.5)


def _liquidity_risk(net_debt: float, revenue: float) -> float:
    """
    Liquidity risk sub-score. Net debt as % of revenue is the key signal.
    """
    if revenue <= 0:
        return 50.0
    ratio = net_debt / revenue
    if ratio > 5:
        return 100.0
    elif ratio > 3:
        return 70 + ((ratio - 3) / 2) * 30
    elif ratio > 1:
        return 40 + ((ratio - 1) / 2) * 30
    elif ratio > 0:
        return ratio * 40
    else:
        # Net cash position — liquidity is a positive signal
        return max(0, 5 + ratio * 5)


def compute_risk_score(
    debt_to_ebitda: float,
    ebitda_margin: float,
    growth_rate: float,
    net_debt: float,
    revenue: float,
    country: str = "",
) -> int:
    """
    Composite risk score (0–100). Higher means riskier.

    Weights:
      Leverage risk    45%
      Margin risk      30%
      Growth risk      15%
      Liquidity risk   10%
    Country risk adds a flat penalty on top (+15 high-risk, +8 medium-risk).

    Args:
        debt_to_ebitda: Debt / EBITDA ratio
        ebitda_margin:  EBITDA margin %
        growth_rate:    YoY revenue growth %
        net_debt:       Total debt - cash (USD)
        revenue:        Annual revenue (USD)
        country:        Country name (optional, for geo-risk)

    Returns:
        risk_score (int, 0–100)
    """
    leverage_r  = _leverage_risk(debt_to_ebitda)
    margin_r    = _margin_risk(ebitda_margin)
    growth_r    = _growth_risk(growth_rate)
    liquidity_r = _liquidity_risk(net_debt, revenue)

    base_risk = (
        leverage_r  * 0.45
        + margin_r  * 0.30
        + growth_r  * 0.15
        + liquidity_r * 0.10
    )

    # Country risk penalty
    country_penalty = 0
    if country in HIGH_RISK_COUNTRIES:
        country_penalty = 15
    elif country in MEDIUM_RISK_COUNTRIES:
        country_penalty = 8

    return min(100, int(base_risk + country_penalty))


def get_risk_label(risk_score: int) -> str:
    """Convert numeric risk score to human-readable label."""
    if risk_score <= 25:
        return "Low"
    elif risk_score <= 50:
        return "Medium"
    elif risk_score <= 70:
        return "High"
    else:
        return "Very High"


def get_risk_factors(  # noqa: C901
    debt_to_ebitda: float,
    ebitda_margin: float,
    growth_rate: float,
    revenue: float,
    country: str = "",
) -> list[dict]:
    """
    Return a structured list of identified risk factors with severity labels.
    Used by the frontend Risk Analysis section.
    """
    factors = []

    # Leverage
    if debt_to_ebitda > 6:
        factors.append({"category": "Leverage", "name": "Excessive Leverage", "severity": "Critical",
            "description": f"Debt/EBITDA of {debt_to_ebitda:.1f}x far exceeds the 5x PE threshold.",
            "mitigation": "Immediate deleveraging plan; refinancing or asset disposals within 24 months."})
    elif debt_to_ebitda > 4:
        factors.append({"category": "Leverage", "name": "High Leverage", "severity": "High",
            "description": f"Debt/EBITDA of {debt_to_ebitda:.1f}x constrains post-acquisition flexibility.",
            "mitigation": "Model accelerated repayment from operating cashflows over 3–5 years."})
    elif debt_to_ebitda > 2.5:
        factors.append({"category": "Leverage", "name": "Moderate Leverage", "severity": "Medium",
            "description": f"Debt/EBITDA of {debt_to_ebitda:.1f}x is manageable but warrants covenant monitoring.",
            "mitigation": "Stress-test covenants against 200bps rate rise scenario."})

    # Profitability
    if ebitda_margin < 5:
        factors.append({"category": "Operational", "name": "Thin Margins", "severity": "High",
            "description": f"EBITDA margin of {ebitda_margin:.1f}% leaves minimal buffer against cost shocks.",
            "mitigation": "SG&A rationalisation and pricing power review within 12 months of close."})
    elif ebitda_margin < 15:
        factors.append({"category": "Operational", "name": "Below-Average Profitability", "severity": "Medium",
            "description": f"Margin of {ebitda_margin:.1f}% is below typical sector benchmarks.",
            "mitigation": "Benchmark against peers; identify top-line pricing and procurement opportunities."})

    # Growth
    if growth_rate < 0:
        factors.append({"category": "Market", "name": "Revenue Contraction", "severity": "Critical",
            "description": f"Revenue declining at {abs(growth_rate):.1f}% YoY — possible structural erosion.",
            "mitigation": "Root-cause analysis before capital commitment; confirm cyclical vs secular."})
    elif growth_rate < 5:
        factors.append({"category": "Market", "name": "Slow Growth", "severity": "Medium",
            "description": f"Revenue growth of {growth_rate:.1f}% is below inflation and GDP growth.",
            "mitigation": "Evaluate adjacency expansion and bolt-on M&A as post-acquisition growth levers."})

    # Scale
    if revenue < 20_000_000:
        factors.append({"category": "Operational", "name": "Sub-Scale Business", "severity": "Medium",
            "description": "Revenue below $20M limits multiple exit routes and strategic buyer interest.",
            "mitigation": "Add-on acquisition strategy to reach $50M+ revenue before exit process."})

    # Country
    if country in HIGH_RISK_COUNTRIES:
        factors.append({"category": "Geopolitical", "name": "High-Risk Jurisdiction", "severity": "High",
            "description": f"{country} carries elevated political, FX, and sanctions risk.",
            "mitigation": "Offshore holdco structure; political risk insurance; FX hedging mandate."})
    elif country in MEDIUM_RISK_COUNTRIES:
        factors.append({"category": "Geopolitical", "name": "Emerging Market Exposure", "severity": "Medium",
            "description": f"{country} presents moderate macro and currency volatility.",
            "mitigation": "Model USD and local-currency IRR scenarios; hedging policy recommended."})

    return factors
