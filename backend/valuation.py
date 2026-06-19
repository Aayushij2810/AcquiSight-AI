"""
AcquiSight AI — Valuation Engine
EV/EBITDA multiples by industry with bear / base / bull scenario ranges.
Imported by routers/screen.py via:
  from valuation import compute_valuation
"""

# ── INDUSTRY MULTIPLE LOOKUP TABLE ───────────────────────────────────────────
# Multiples are blended EV/EBITDA benchmarks sourced from public market data.
# Bear = 25th pct, Base = median, Bull = 75th pct of peer group.

MULTIPLES: dict[str, dict] = {
    "SaaS":             {"bear": 14, "base": 22, "bull": 35},
    "Fintech":          {"bear": 12, "base": 18, "bull": 28},
    "Healthcare":       {"bear": 10, "base": 14, "bull": 20},
    "Manufacturing":    {"bear": 6,  "base": 9,  "bull": 12},
    "Consumer":         {"bear": 7,  "base": 10, "bull": 14},
    "Energy":           {"bear": 4,  "base": 6,  "bull": 9},
    "Real Estate":      {"bear": 8,  "base": 12, "bull": 16},
    "Technology":       {"bear": 12, "base": 18, "bull": 30},
    "Retail":           {"bear": 5,  "base": 8,  "bull": 11},
    "Other":            {"bear": 7,  "base": 10, "bull": 14},
}

# Revenue multiples as secondary cross-check (EV/Revenue)
REVENUE_MULTIPLES: dict[str, dict] = {
    "SaaS":             {"bear": 5,   "base": 8,   "bull": 14},
    "Fintech":          {"bear": 3,   "base": 6,   "bull": 10},
    "Healthcare":       {"bear": 1.5, "base": 3,   "bull": 5},
    "Manufacturing":    {"bear": 0.6, "base": 1.0, "bull": 1.6},
    "Consumer":         {"bear": 0.8, "base": 1.5, "bull": 2.5},
    "Energy":           {"bear": 0.4, "base": 0.8, "bull": 1.4},
    "Real Estate":      {"bear": 1.5, "base": 3.0, "bull": 5.5},
    "Technology":       {"bear": 3,   "base": 6,   "bull": 12},
    "Retail":           {"bear": 0.3, "base": 0.6, "bull": 1.0},
    "Other":            {"bear": 0.8, "base": 1.8, "bull": 3.2},
}


def compute_valuation(ebitda: float, revenue: float, industry: str) -> float:
    """
    Return base-case Enterprise Value (USD) using a blended
    60% EV/EBITDA + 40% EV/Revenue approach.

    Args:
        ebitda:   LTM EBITDA in USD
        revenue:  LTM Revenue in USD
        industry: Industry string matching the Industry enum values

    Returns:
        Enterprise Value (float, USD)
    """
    em = MULTIPLES.get(industry, MULTIPLES["Other"])
    rm = REVENUE_MULTIPLES.get(industry, REVENUE_MULTIPLES["Other"])

    ev_ebitda_base = ebitda * em["base"]
    ev_revenue_base = revenue * rm["base"]

    # Blended base-case EV
    blended_ev = ev_ebitda_base * 0.60 + ev_revenue_base * 0.40
    return round(blended_ev, 2)


def compute_valuation_range(ebitda: float, revenue: float, industry: str) -> dict:
    """
    Return bear / base / bull EV range using both multiples.
    Useful for frontend chart rendering.

    Returns:
        {"bear": float, "base": float, "bull": float}
    """
    em = MULTIPLES.get(industry, MULTIPLES["Other"])
    rm = REVENUE_MULTIPLES.get(industry, REVENUE_MULTIPLES["Other"])

    return {
        "bear": round(ebitda * em["bear"] * 0.6 + revenue * rm["bear"] * 0.4, 2),
        "base": round(ebitda * em["base"] * 0.6 + revenue * rm["base"] * 0.4, 2),
        "bull": round(ebitda * em["bull"] * 0.6 + revenue * rm["bull"] * 0.4, 2),
    }


def get_multiples_for_industry(industry: str) -> dict:
    """Expose EV/EBITDA multiples for a given industry (used in comps table)."""
    return {
        "ev_ebitda": MULTIPLES.get(industry, MULTIPLES["Other"]),
        "ev_revenue": REVENUE_MULTIPLES.get(industry, REVENUE_MULTIPLES["Other"]),
    }
