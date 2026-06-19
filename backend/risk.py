"""
AcquiSight AI — Risk Scoring Engine
Five risk dimensions with weighted composite and mandatory risk drivers.
"""

from __future__ import annotations

from models import RiskBreakdownItem, RiskFactor

HIGH_RISK_COUNTRIES = {
    "Russia", "Venezuela", "Iran", "North Korea", "Belarus",
    "Myanmar", "Sudan", "Syria", "Libya", "Yemen",
}
MEDIUM_RISK_COUNTRIES = {
    "Argentina", "Turkey", "Pakistan", "Nigeria", "Egypt",
    "Ukraine", "Ethiopia", "Bangladesh", "Iraq", "Lebanon",
}

RISK_WEIGHTS: dict[str, float] = {
    "revenue_growth": 0.20,
    "leverage": 0.25,
    "profitability": 0.20,
    "customer_concentration": 0.15,
    "industry": 0.20,
}

INDUSTRY_RISK_BASE: dict[str, float] = {
    "SaaS": 30,
    "Fintech": 35,
    "Healthcare": 28,
    "Manufacturing": 32,
    "Consumer": 30,
    "Energy": 38,
    "Real Estate": 34,
    "Technology": 32,
    "Retail": 36,
    "Telecommunications": 34,
    "Media & Entertainment": 36,
    "Logistics & Transportation": 35,
    "Pharmaceuticals & Biotech": 30,
    "Insurance": 28,
    "Automotive": 37,
    "Aerospace & Defense": 33,
    "Education": 32,
    "Hospitality & Leisure": 40,
    "Cybersecurity": 31,
    "E-Commerce": 35,
    "Industrial Services": 33,
    "Other": 33,
}


def _revenue_growth_risk(growth_rate: float) -> float:
    if growth_rate < -10:
        return 95.0
    if growth_rate < 0:
        return 75 + ((0 - growth_rate) / 10) * 20
    if growth_rate < 5:
        return 50 + ((5 - growth_rate) / 5) * 25
    if growth_rate < 10:
        return 30 + ((10 - growth_rate) / 5) * 20
    if growth_rate < 20:
        return 12 + ((20 - growth_rate) / 10) * 18
    return max(5, 12 - (growth_rate - 20) * 0.3)


def _leverage_risk(debt_to_ebitda: float) -> float:
    if debt_to_ebitda >= 7:
        return 95.0
    if debt_to_ebitda >= 5:
        return 75 + ((debt_to_ebitda - 5) / 2) * 20
    if debt_to_ebitda >= 3:
        return 50 + ((debt_to_ebitda - 3) / 2) * 25
    if debt_to_ebitda >= 2:
        return 30 + ((debt_to_ebitda - 2) / 1) * 20
    if debt_to_ebitda >= 1:
        return 12 + ((debt_to_ebitda - 1) / 1) * 18
    return max(3, debt_to_ebitda * 10)


def _profitability_risk(ebitda_margin: float) -> float:
    if ebitda_margin < 0:
        return 95.0
    if ebitda_margin < 5:
        return 70 + ((5 - ebitda_margin) / 5) * 25
    if ebitda_margin < 15:
        return 45 + ((15 - ebitda_margin) / 10) * 25
    if ebitda_margin < 25:
        return 20 + ((25 - ebitda_margin) / 10) * 25
    return max(5, 18 - (ebitda_margin - 25) * 0.35)


def _customer_concentration_risk(revenue: float) -> float:
    """Proxy: smaller companies typically face higher customer concentration risk."""
    if revenue >= 50_000_000_000:
        return 10.0
    if revenue >= 10_000_000_000:
        return 18.0
    if revenue >= 1_000_000_000:
        return 30.0
    if revenue >= 100_000_000:
        return 48.0
    if revenue >= 20_000_000:
        return 62.0
    return 78.0


def _industry_risk(industry: str, country: str) -> float:
    base = INDUSTRY_RISK_BASE.get(industry, INDUSTRY_RISK_BASE["Other"])
    if country in HIGH_RISK_COUNTRIES:
        return min(100, base + 25)
    if country in MEDIUM_RISK_COUNTRIES:
        return min(100, base + 12)
    return base


def get_risk_label(risk_score: int) -> str:
    if risk_score <= 20:
        return "Very Low Risk"
    if risk_score <= 40:
        return "Low Risk"
    if risk_score <= 60:
        return "Moderate Risk"
    if risk_score <= 80:
        return "High Risk"
    return "Very High Risk"


def compute_risk_assessment(
    debt_to_ebitda: float,
    ebitda_margin: float,
    growth_rate: float,
    revenue: float,
    industry: str,
    country: str = "",
) -> tuple[int, str, list[RiskBreakdownItem], list[RiskFactor]]:
    sub_scores = {
        "revenue_growth": _revenue_growth_risk(growth_rate),
        "leverage": _leverage_risk(debt_to_ebitda),
        "profitability": _profitability_risk(ebitda_margin),
        "customer_concentration": _customer_concentration_risk(revenue),
        "industry": _industry_risk(industry, country),
    }

    labels = {
        "revenue_growth": "Revenue Growth Risk",
        "leverage": "Leverage Risk",
        "profitability": "Profitability Risk",
        "customer_concentration": "Customer Concentration Risk",
        "industry": "Industry Risk",
    }

    breakdown: list[RiskBreakdownItem] = []
    total = 0.0
    for key, weight in RISK_WEIGHTS.items():
        contribution = sub_scores[key] * weight
        total += contribution
        breakdown.append(
            RiskBreakdownItem(
                dimension=labels[key],
                sub_score=round(sub_scores[key], 1),
                weight_pct=weight * 100,
                weighted_contribution=round(contribution, 2),
            )
        )

    risk_score = min(100, int(round(total)))
    factors = _build_risk_factors(
        debt_to_ebitda=debt_to_ebitda,
        ebitda_margin=ebitda_margin,
        growth_rate=growth_rate,
        revenue=revenue,
        industry=industry,
        country=country,
        sub_scores=sub_scores,
    )

    return risk_score, get_risk_label(risk_score), breakdown, factors


def _build_risk_factors(
    debt_to_ebitda: float,
    ebitda_margin: float,
    growth_rate: float,
    revenue: float,
    industry: str,
    country: str,
    sub_scores: dict[str, float],
) -> list[RiskFactor]:
    factors: list[RiskFactor] = []

    if growth_rate < 0:
        factors.append(RiskFactor(
            category="Revenue Growth",
            name="Revenue Contraction",
            severity="Critical",
            description=f"Revenue declining at {abs(growth_rate):.1f}% YoY signals potential structural headwinds.",
            mitigation="Distinguish cyclical vs secular decline before committing capital.",
        ))
    elif growth_rate < 5:
        factors.append(RiskFactor(
            category="Revenue Growth",
            name="Below-Trend Growth",
            severity="Medium",
            description=f"Revenue growth of {growth_rate:.1f}% trails GDP and inflation benchmarks.",
            mitigation="Model organic vs inorganic growth; stress-test flat revenue scenarios.",
        ))
    else:
        factors.append(RiskFactor(
            category="Revenue Growth",
            name="Growth Deceleration Risk",
            severity="Low" if growth_rate >= 15 else "Medium",
            description=f"At {growth_rate:.1f}% YoY growth, sustaining momentum as revenue base scales remains a key risk.",
            mitigation="Monitor pipeline conversion, churn, and pricing power quarterly.",
        ))

    if debt_to_ebitda > 5:
        factors.append(RiskFactor(
            category="Leverage",
            name="Elevated Leverage",
            severity="High" if debt_to_ebitda > 6 else "Medium",
            description=f"Debt/EBITDA of {debt_to_ebitda:.1f}x limits financial flexibility and covenant headroom.",
            mitigation="Structure deleveraging covenants; model 200bps rate shock on interest coverage.",
        ))
    elif debt_to_ebitda > 2:
        factors.append(RiskFactor(
            category="Leverage",
            name="Moderate Leverage",
            severity="Medium",
            description=f"Debt/EBITDA of {debt_to_ebitda:.1f}x is manageable but warrants ongoing covenant monitoring.",
            mitigation="Stress-test covenants against rate rises and EBITDA downturn scenarios.",
        ))
    else:
        factors.append(RiskFactor(
            category="Leverage",
            name="Balance Sheet Optionality",
            severity="Low",
            description=f"Net leverage of {debt_to_ebitda:.1f}x provides balance-sheet flexibility but limits downside protection in downturns.",
            mitigation="Evaluate optimal capital structure for shareholder returns vs acquisition capacity.",
        ))

    if ebitda_margin < 10:
        factors.append(RiskFactor(
            category="Profitability",
            name="Margin Compression Risk",
            severity="High" if ebitda_margin < 5 else "Medium",
            description=f"EBITDA margin of {ebitda_margin:.1f}% offers limited buffer against cost inflation.",
            mitigation="Benchmark unit economics vs peers; identify SG&A and procurement levers.",
        ))
    else:
        factors.append(RiskFactor(
            category="Profitability",
            name="Margin Sustainability",
            severity="Low",
            description=f"EBITDA margin of {ebitda_margin:.1f}% is healthy but subject to competitive and input-cost pressure.",
            mitigation="Track gross margin trends and operating leverage through the cycle.",
        ))

    if revenue < 100_000_000:
        factors.append(RiskFactor(
            category="Customer Concentration",
            name="Customer Concentration Exposure",
            severity="High",
            description="Sub-$100M revenue base typically implies concentrated customer or contract exposure.",
            mitigation="Obtain top-10 customer revenue breakdown; model loss of largest account.",
        ))
    elif revenue < 1_000_000_000:
        factors.append(RiskFactor(
            category="Customer Concentration",
            name="Mid-Market Concentration Risk",
            severity="Medium",
            description="Mid-market scale may still carry meaningful customer or channel concentration.",
            mitigation="Request customer cohort analysis and contract renewal schedules in diligence.",
        ))
    else:
        factors.append(RiskFactor(
            category="Customer Concentration",
            name="Enterprise / Segment Concentration",
            severity="Low",
            description="Large revenue base reduces single-customer risk, but segment or geographic concentration may persist.",
            mitigation="Review revenue by segment, geography, and product line in CIM data room.",
        ))

    factors.append(RiskFactor(
        category="Industry",
        name=f"{industry} Sector Risk",
        severity="Medium" if sub_scores["industry"] >= 35 else "Low",
        description=(
            f"{industry} faces sector-specific competitive, regulatory, and technology disruption dynamics "
            f"(industry risk sub-score: {sub_scores['industry']:.0f}/100)."
        ),
        mitigation="Benchmark against sector peers; model regulatory and competitive scenario cases.",
    ))

    if revenue >= 50_000_000_000:
        factors.append(RiskFactor(
            category="Scale",
            name="Mega-Cap Acquisition Constraints",
            severity="Medium",
            description="Revenue scale above $50B makes full buyout impractical for traditional PE; only strategic or public-market actions feasible.",
            mitigation="Evaluate minority stakes, spin-offs, or public-market positioning rather than LBO.",
        ))

    if country in HIGH_RISK_COUNTRIES:
        factors.append(RiskFactor(
            category="Geopolitical",
            name="High-Risk Jurisdiction",
            severity="High",
            description=f"Operations or exposure in {country} carry elevated political, FX, and sanctions risk.",
            mitigation="Offshore holdco structure; political risk insurance; FX hedging mandate.",
        ))
    elif country in MEDIUM_RISK_COUNTRIES:
        factors.append(RiskFactor(
            category="Geopolitical",
            name="Emerging Market Exposure",
            severity="Medium",
            description=f"{country} presents moderate macro and currency volatility.",
            mitigation="Model USD and local-currency IRR scenarios; hedging policy recommended.",
        ))

    return factors
