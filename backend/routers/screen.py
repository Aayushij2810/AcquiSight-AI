"""
POST /api/screen  —  Main deal-screening endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json

from models import DealScreenRequest, DealScreenResponse
from scoring import compute_scores
from valuation import compute_valuation
from risk import compute_risk_score
from comps import get_comps
from database import get_db, ScreenedDeal

router = APIRouter()


@router.post("/screen", response_model=DealScreenResponse)
def screen_deal(payload: DealScreenRequest, db: Session = Depends(get_db)):
    """
    Screen a company and return investment scores, valuation, risk, and comps.
    Results are persisted to PostgreSQL for history tracking.
    """
    try:
        # 1. Derived financial metrics
        ebitda_margin = (payload.ebitda / payload.revenue) * 100 if payload.revenue else 0.0
        net_debt = payload.debt - payload.cash
        debt_to_ebitda = (payload.debt / payload.ebitda) if payload.ebitda > 0 else None

        # 2. Valuation
        ev = compute_valuation(
            ebitda=payload.ebitda,
            revenue=payload.revenue,
            industry=payload.industry.value,
        )

        # 3. Scores
        scores, investment_score = compute_scores(
            ebitda_margin=ebitda_margin,
            growth_rate=payload.growth_rate,
            debt_to_ebitda=debt_to_ebitda if debt_to_ebitda is not None else 99,
            revenue=payload.revenue,
            cash=payload.cash,
            debt=payload.debt,
            industry=payload.industry.value,
        )

        # 4. Risk score
        risk_score = compute_risk_score(
            debt_to_ebitda=debt_to_ebitda if debt_to_ebitda is not None else 99,
            ebitda_margin=ebitda_margin,
            growth_rate=payload.growth_rate,
            net_debt=net_debt,
            revenue=payload.revenue,
        )

        # 5. Comps
        comps_result = get_comps(
            industry=payload.industry.value,
            ebitda=payload.ebitda,
        )

        # 6. Recommendation
        rec, rec_color = _recommend(investment_score)

        response = DealScreenResponse(
            company_name=payload.company_name,
            industry=payload.industry.value,
            ebitda_margin=round(ebitda_margin, 2),
            net_debt=net_debt,
            debt_to_ebitda=round(debt_to_ebitda, 2) if debt_to_ebitda is not None else None,
            enterprise_value=ev,
            investment_score=investment_score,
            risk_score=risk_score,
            scores=scores,
            recommendation=rec,
            recommendation_color=rec_color,
            comps=comps_result,
        )

        # 7. Persist to DB
        deal = ScreenedDeal(
            company_name=payload.company_name,
            industry=payload.industry.value,
            country=payload.country,
            revenue=payload.revenue,
            ebitda=payload.ebitda,
            growth_rate=payload.growth_rate,
            debt=payload.debt,
            cash=payload.cash,
            ebitda_margin=ebitda_margin,
            enterprise_value=ev,
            investment_score=investment_score,
            risk_score=risk_score,
            recommendation=rec,
            scores_json=scores.model_dump(),
            comps_json=comps_result.model_dump(),
        )
        db.add(deal)
        db.commit()

        return response

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def _recommend(score: int) -> tuple[str, str]:
    """Map investment score to recommendation text and UI color."""
    if score >= 80:
        return "Strong Buyout Candidate", "#22c55e"     # green-500
    elif score >= 65:
        return "Attractive Growth Investment", "#3b82f6"  # blue-500
    elif score >= 50:
        return "Requires Further Due Diligence", "#eab308"  # yellow-500
    elif score >= 35:
        return "High Risk Opportunity", "#f97316"          # orange-500
    else:
        return "Reject", "#ef4444"                         # red-500
