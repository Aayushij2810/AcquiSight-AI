"""
AcquiSight AI — Investment Scoring Engine
All scoring functions. Imported by routers/screen.py via:
  from scoring import compute_scores
"""

from models import DimensionScores

# ── INDUSTRY PROFILE WEIGHTS ─────────────────────────────────────────────────
# Different industries have different value drivers, so we weight the five
# scoring dimensions accordingly.

INDUSTRY_WEIGHTS: dict[str, dict] = {
    "SaaS": {"growth": 0.35, "profitability": 0.20, "leverage": 0.20, "revenue_quality": 0.15, "financial_health": 0.10},
    "Fintech": {"growth": 0.30, "profitability": 0.25, "leverage": 0.20, "revenue_quality": 0.15, "financial_health": 0.10},
    "Healthcare": {"growth": 0.20, "profitability": 0.30, "leverage": 0.20, "revenue_quality": 0.15, "financial_health": 0.15},
    "Manufacturing": {"growth": 0.15, "profitability": 0.25, "leverage": 0.25, "revenue_quality": 0.15, "financial_health": 0.20},
    "Consumer": {"growth": 0.20, "profitability": 0.30, "leverage": 0.20, "revenue_quality": 0.20, "financial_health": 0.10},
    "Energy": {"growth": 0.15, "profitability": 0.25, "leverage": 0.25, "revenue_quality": 0.15, "financial_health": 0.20},
    "Real Estate": {"growth": 0.10, "profitability": 0.30, "leverage": 0.30, "revenue_quality": 0.15, "financial_health": 0.15},
    "Technology": {"growth": 0.35, "profitability": 0.20, "leverage": 0.20, "revenue_quality": 0.15, "financial_health": 0.10},
    "Retail": {"growth": 0.20, "profitability": 0.30, "leverage": 0.20, "revenue_quality": 0.20, "financial_health": 0.10},
    "Other": {"growth": 0.25, "profitability": 0.25, "leverage": 0.20, "revenue_quality": 0.15, "financial_health": 0.15},
}


# ── DIMENSION SCORERS ────────────────────────────────────────────────────────

def _score_growth(growth_rate: float) -> int:
    """
    Revenue growth score (0–100).
    >30%   → 100
    20–30% → 80–100
    10–20% → 60–80
    5–10%  → 40–60
    0–5%   → 20–40
    <0%    → 0–20  (negative growth penalised)
    """
    if growth_rate >= 30:
        return 100
    elif growth_rate >= 20:
        return int(80 + ((growth_rate - 20) / 10) * 20)
    elif growth_rate >= 10:
        return int(60 + ((growth_rate - 10) / 10) * 20)
    elif growth_rate >= 5:
        return int(40 + ((growth_rate - 5) / 5) * 20)
    elif growth_rate >= 0:
        return int(20 + (growth_rate / 5) * 20)
    else:
        return max(0, int(20 + growth_rate * 2))


def _score_profitability(ebitda_margin: float) -> int:
    """
    EBITDA margin score (0–100).
    >40%   → 100
    25–40% → 75–100
    15–25% → 50–75
    5–15%  → 25–50
    <5%    → 0–25
    """
    if ebitda_margin >= 40:
        return 100
    elif ebitda_margin >= 25:
        return int(75 + ((ebitda_margin - 25) / 15) * 25)
    elif ebitda_margin >= 15:
        return int(50 + ((ebitda_margin - 15) / 10) * 25)
    elif ebitda_margin >= 5:
        return int(25 + ((ebitda_margin - 5) / 10) * 25)
    else:
        return max(0, int(ebitda_margin * 5))


def _score_leverage(debt_to_ebitda: float) -> int:
    """
    Leverage score (0–100). Lower leverage = higher score.
    <1x   → 100
    1–2x  → 80–100
    2–3x  → 60–80
    3–5x  → 30–60
    5–7x  → 10–30
    >7x   → 0–10
    """
    if debt_to_ebitda < 1:
        return 100
    elif debt_to_ebitda < 2:
        return int(100 - ((debt_to_ebitda - 1) / 1) * 20)
    elif debt_to_ebitda < 3:
        return int(80 - ((debt_to_ebitda - 2) / 1) * 20)
    elif debt_to_ebitda < 5:
        return int(60 - ((debt_to_ebitda - 3) / 2) * 30)
    elif debt_to_ebitda < 7:
        return int(30 - ((debt_to_ebitda - 5) / 2) * 20)
    else:
        return max(0, int(10 - (debt_to_ebitda - 7) * 2))


def _score_revenue_quality(revenue: float, ebitda_margin: float, growth_rate: float) -> int:
    """
    Revenue quality score (0–100): combines scale, margin sustainability, growth trajectory.
    """
    # Scale (0–33)
    if revenue >= 1_000_000_000:
        scale = 33
    elif revenue >= 100_000_000:
        scale = int(20 + ((revenue - 100_000_000) / 900_000_000) * 13)
    elif revenue >= 10_000_000:
        scale = int(10 + ((revenue - 10_000_000) / 90_000_000) * 10)
    else:
        scale = int(revenue / 10_000_000 * 10)

    # Margin sustainability (0–34)
    margin_component = min(34, int(ebitda_margin * 0.85))

    # Growth trajectory (0–33)
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
    """
    Financial health score (0–100): profitability × 40% + leverage × 40% + liquidity × 20%.
    """
    profitability = _score_profitability(ebitda_margin) * 0.40
    leverage = _score_leverage(debt_to_ebitda) * 0.40
    cash_ratio = (cash / revenue * 100) if revenue > 0 else 0
    liquidity = min(100, cash_ratio * 5) * 0.20
    return min(100, int(profitability + leverage + liquidity))


# ── PUBLIC API ────────────────────────────────────────────────────────────────

def compute_scores(
    ebitda_margin: float,
    growth_rate: float,
    debt_to_ebitda: float,
    revenue: float,
    cash: float,
    debt: float,
    industry: str,
) -> tuple[DimensionScores, int]:
    """
    Compute all five dimension scores and the weighted composite investment score.

    Returns:
        (DimensionScores, investment_score: int)
    """
    growth = _score_growth(growth_rate)
    profitability = _score_profitability(ebitda_margin)
    leverage = _score_leverage(debt_to_ebitda)
    revenue_quality = _score_revenue_quality(revenue, ebitda_margin, growth_rate)
    financial_health = _score_financial_health(ebitda_margin, debt_to_ebitda, cash, revenue)

    weights = INDUSTRY_WEIGHTS.get(industry, INDUSTRY_WEIGHTS["Other"])

    investment_score = int(
        growth * weights["growth"]
        + profitability * weights["profitability"]
        + leverage * weights["leverage"]
        + revenue_quality * weights["revenue_quality"]
        + financial_health * weights["financial_health"]
    )

    scores = DimensionScores(
        growth=growth,
        profitability=profitability,
        leverage=leverage,
        revenue_quality=revenue_quality,
        financial_health=financial_health,
    )

    return scores, min(100, investment_score)
