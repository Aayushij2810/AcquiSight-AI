"""
AcquiSight AI — Investment Scoring Engine
Fixed-weight composite score with full transparency breakdown.
"""

from models import DimensionScores, ScoreBreakdownItem

# Standard PE screening weights (sum = 100%)
DIMENSION_WEIGHTS: dict[str, float] = {
    "growth": 0.20,
    "profitability": 0.25,
    "leverage": 0.20,
    "revenue_quality": 0.15,
    "financial_health": 0.20,
}

DIMENSION_LABELS: dict[str, str] = {
    "growth": "Growth",
    "profitability": "Profitability",
    "leverage": "Leverage",
    "revenue_quality": "Revenue Quality",
    "financial_health": "Financial Health",
}


def _score_growth(growth_rate: float) -> int:
    if growth_rate >= 30:
        return 100
    if growth_rate >= 20:
        return int(80 + ((growth_rate - 20) / 10) * 20)
    if growth_rate >= 10:
        return int(60 + ((growth_rate - 10) / 10) * 20)
    if growth_rate >= 5:
        return int(40 + ((growth_rate - 5) / 5) * 20)
    if growth_rate >= 0:
        return int(20 + (growth_rate / 5) * 20)
    return max(0, int(20 + growth_rate * 2))


def _score_profitability(ebitda_margin: float) -> int:
    if ebitda_margin >= 40:
        return 100
    if ebitda_margin >= 25:
        return int(75 + ((ebitda_margin - 25) / 15) * 25)
    if ebitda_margin >= 15:
        return int(50 + ((ebitda_margin - 15) / 10) * 25)
    if ebitda_margin >= 5:
        return int(25 + ((ebitda_margin - 5) / 10) * 25)
    return max(0, int(ebitda_margin * 5))


def _score_leverage(debt_to_ebitda: float) -> int:
    if debt_to_ebitda < 1:
        return 100
    if debt_to_ebitda < 2:
        return int(100 - ((debt_to_ebitda - 1) / 1) * 20)
    if debt_to_ebitda < 3:
        return int(80 - ((debt_to_ebitda - 2) / 1) * 20)
    if debt_to_ebitda < 5:
        return int(60 - ((debt_to_ebitda - 3) / 2) * 30)
    if debt_to_ebitda < 7:
        return int(30 - ((debt_to_ebitda - 5) / 2) * 20)
    return max(0, int(10 - (debt_to_ebitda - 7) * 2))


def _score_revenue_quality(revenue: float, ebitda_margin: float, growth_rate: float) -> int:
    if revenue >= 1_000_000_000:
        scale = 33
    elif revenue >= 100_000_000:
        scale = int(20 + ((revenue - 100_000_000) / 900_000_000) * 13)
    elif revenue >= 10_000_000:
        scale = int(10 + ((revenue - 10_000_000) / 90_000_000) * 10)
    else:
        scale = int(revenue / 10_000_000 * 10)

    margin_component = min(34, int(ebitda_margin * 0.85))

    if growth_rate >= 20:
        growth_component = 33
    elif growth_rate >= 10:
        growth_component = int(22 + ((growth_rate - 10) / 10) * 11)
    elif growth_rate >= 0:
        growth_component = int(growth_rate * 2.2)
    else:
        growth_component = max(0, int(5 + growth_rate))

    return min(100, scale + margin_component + growth_component)


def _score_financial_health(
    ebitda_margin: float,
    debt_to_ebitda: float,
    cash: float,
    revenue: float,
) -> int:
    profitability = _score_profitability(ebitda_margin) * 0.40
    leverage = _score_leverage(debt_to_ebitda) * 0.40
    cash_ratio = (cash / revenue * 100) if revenue > 0 else 0
    liquidity = min(100, cash_ratio * 5) * 0.20
    return min(100, int(profitability + leverage + liquidity))


def compute_scores(
    ebitda_margin: float,
    growth_rate: float,
    debt_to_ebitda: float,
    revenue: float,
    cash: float,
    debt: float,
    industry: str,
) -> tuple[DimensionScores, int, list[ScoreBreakdownItem]]:
    """
    Compute dimension scores and weighted investment score.

    Investment Score =
        (Growth × 20%) + (Profitability × 25%) + (Leverage × 20%)
        + (Revenue Quality × 15%) + (Financial Health × 20%)
    """
    del industry, debt  # fixed weights; inputs retained for API compatibility

    raw = {
        "growth": _score_growth(growth_rate),
        "profitability": _score_profitability(ebitda_margin),
        "leverage": _score_leverage(debt_to_ebitda),
        "revenue_quality": _score_revenue_quality(revenue, ebitda_margin, growth_rate),
        "financial_health": _score_financial_health(ebitda_margin, debt_to_ebitda, cash, revenue),
    }

    breakdown: list[ScoreBreakdownItem] = []
    investment_score = 0.0

    for key, weight in DIMENSION_WEIGHTS.items():
        contribution = raw[key] * weight
        investment_score += contribution
        breakdown.append(
            ScoreBreakdownItem(
                dimension=DIMENSION_LABELS[key],
                raw_score=raw[key],
                weight_pct=weight * 100,
                weighted_contribution=round(contribution, 2),
                formula=f"{raw[key]} × {weight:.0%} = {contribution:.2f}",
            )
        )

    scores = DimensionScores(
        growth=raw["growth"],
        profitability=raw["profitability"],
        leverage=raw["leverage"],
        revenue_quality=raw["revenue_quality"],
        financial_health=raw["financial_health"],
    )

    return scores, min(100, int(round(investment_score))), breakdown
