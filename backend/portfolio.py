"""Portfolio scoring and analytics helpers."""

from __future__ import annotations

from collections import Counter
from typing import Any

PIPELINE_STAGES = [
    "Sourced",
    "Screening",
    "Due Diligence",
    "Investment Committee",
    "Approved",
    "Rejected",
]


def compute_priority_score(investment_score: int, risk_score: int) -> float:
    """Priority = (Investment Score × 60%) + (100 − Risk Score) × 40%"""
    return round(investment_score * 0.60 + (100 - risk_score) * 0.40, 2)


def opportunity_to_dict(opp: Any) -> dict:
    return {
        "id": opp.id,
        "company_name": opp.company_name,
        "industry": opp.industry,
        "revenue": opp.revenue,
        "ebitda": opp.ebitda,
        "growth_rate": opp.growth_rate,
        "debt": opp.debt,
        "cash": opp.cash,
        "investment_score": opp.investment_score,
        "risk_score": opp.risk_score,
        "recommendation": opp.recommendation,
        "enterprise_value": opp.enterprise_value,
        "priority_score": opp.priority_score,
        "date_added": opp.date_added.isoformat() if opp.date_added else None,
        "status": opp.status,
        "notes": opp.notes or "",
        "watchlist": bool(opp.watchlist),
        "ic_decision": opp.ic_decision,
        "screen_result": opp.screen_result_json,
        "memo": opp.memo_json,
    }


def build_analytics(opportunities: list[Any]) -> dict:
    if not opportunities:
        return {
            "total_opportunities": 0,
            "avg_investment_score": 0,
            "avg_risk_score": 0,
            "total_enterprise_value": 0,
            "highest_scoring": None,
            "lowest_risk": None,
            "industries_represented": 0,
            "industry_breakdown": [],
            "stage_breakdown": [],
            "investment_score_distribution": [],
            "risk_score_distribution": [],
            "ev_distribution": [],
            "growth_risk_scatter": [],
            "highlights": {
                "best_opportunity": None,
                "most_undervalued": None,
                "highest_growth": None,
                "safest_investment": None,
            },
            "watchlist_top_scores": [],
            "watchlist_lowest_risk": [],
            "watchlist_fastest_growth": [],
        }

    total = len(opportunities)
    avg_inv = round(sum(o.investment_score for o in opportunities) / total, 1)
    avg_risk = round(sum(o.risk_score for o in opportunities) / total, 1)
    total_ev = sum(o.enterprise_value for o in opportunities)

    highest = max(opportunities, key=lambda o: o.investment_score)
    lowest_risk = min(opportunities, key=lambda o: o.risk_score)
    industries = len({o.industry for o in opportunities})

    industry_counts = Counter(o.industry for o in opportunities)
    stage_counts = Counter(o.status for o in opportunities)

    def bucket(values: list[float], bins: list[tuple[int, int, str]]) -> list[dict]:
        result = []
        for lo, hi, label in bins:
            count = sum(1 for v in values if lo <= v <= hi)
            result.append({"label": label, "count": count})
        return result

    inv_dist = bucket(
        [o.investment_score for o in opportunities],
        [(0, 39, "0–39"), (40, 59, "40–59"), (60, 79, "60–79"), (80, 100, "80–100")],
    )
    risk_dist = bucket(
        [o.risk_score for o in opportunities],
        [(0, 20, "0–20"), (21, 40, "21–40"), (41, 60, "41–60"), (61, 80, "61–80"), (81, 100, "81–100")],
    )
    ev_values = [o.enterprise_value for o in opportunities]
    ev_max = max(ev_values) if ev_values else 1
    ev_dist = bucket(
        ev_values,
        [
            (0, ev_max * 0.25, "Low"),
            (ev_max * 0.25, ev_max * 0.50, "Mid-Low"),
            (ev_max * 0.50, ev_max * 0.75, "Mid-High"),
            (ev_max * 0.75, ev_max * 1.01, "High"),
        ],
    )

    scatter = [
        {
            "company_name": o.company_name,
            "growth_rate": o.growth_rate,
            "risk_score": o.risk_score,
            "investment_score": o.investment_score,
        }
        for o in opportunities
    ]

    best = max(opportunities, key=lambda o: o.priority_score)
    safest = min(opportunities, key=lambda o: o.risk_score)
    highest_growth = max(opportunities, key=lambda o: o.growth_rate)
    most_undervalued = min(
        opportunities,
        key=lambda o: o.enterprise_value / o.ebitda if o.ebitda > 0 else float("inf"),
    )

    watchlist = [o for o in opportunities if o.watchlist]
    top_scores = sorted(opportunities, key=lambda o: o.investment_score, reverse=True)[:5]
    lowest_risk_list = sorted(opportunities, key=lambda o: o.risk_score)[:5]
    fastest_growth = sorted(opportunities, key=lambda o: o.growth_rate, reverse=True)[:5]

    def brief(o: Any) -> dict:
        return {
            "id": o.id,
            "company_name": o.company_name,
            "industry": o.industry,
            "investment_score": o.investment_score,
            "risk_score": o.risk_score,
            "growth_rate": o.growth_rate,
            "enterprise_value": o.enterprise_value,
            "priority_score": o.priority_score,
            "recommendation": o.recommendation,
            "status": o.status,
        }

    return {
        "total_opportunities": total,
        "avg_investment_score": avg_inv,
        "avg_risk_score": avg_risk,
        "total_enterprise_value": total_ev,
        "highest_scoring": brief(highest),
        "lowest_risk": brief(lowest_risk),
        "industries_represented": industries,
        "industry_breakdown": [{"industry": k, "count": v} for k, v in industry_counts.items()],
        "stage_breakdown": [{"stage": k, "count": v} for k, v in stage_counts.items()],
        "investment_score_distribution": inv_dist,
        "risk_score_distribution": risk_dist,
        "ev_distribution": ev_dist,
        "growth_risk_scatter": scatter,
        "highlights": {
            "best_opportunity": brief(best),
            "most_undervalued": brief(most_undervalued),
            "highest_growth": brief(highest_growth),
            "safest_investment": brief(safest),
        },
        "watchlist_top_scores": [brief(o) for o in top_scores],
        "watchlist_lowest_risk": [brief(o) for o in lowest_risk_list],
        "watchlist_fastest_growth": [brief(o) for o in fastest_growth],
        "watchlist_count": len(watchlist),
    }
