"""
POST /api/screen  —  Main deal-screening endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import DealScreenRequest, DealScreenResponse
from scoring import compute_scores
from valuation import compute_enterprise_value
from risk import compute_risk_assessment
from comps import get_comps
from recommendation import get_recommendation
from database import get_db, ScreenedDeal

router = APIRouter()


@router.post("/screen", response_model=DealScreenResponse)
def screen_deal(payload: DealScreenRequest, db: Session = Depends(get_db)):
    """
    Screen a company and return investment scores, valuation, risk, and comps.
    Results are persisted to PostgreSQL for history tracking.
    """
    try:
        ebitda_margin = (payload.ebitda / payload.revenue) * 100 if payload.revenue else 0.0
        net_debt = payload.debt - payload.cash
        debt_to_ebitda = (payload.debt / payload.ebitda) if payload.ebitda > 0 else None
        dte = debt_to_ebitda if debt_to_ebitda is not None else 99.0

        comps_result = get_comps(
            industry=payload.industry.value,
            ebitda=payload.ebitda,
        )

        valuation = compute_enterprise_value(
            ebitda=payload.ebitda,
            debt=payload.debt,
            cash=payload.cash,
            industry=payload.industry.value,
            market_cap=payload.market_cap,
            base_multiple=comps_result.base_multiple,
        )

        scores, investment_score, score_breakdown = compute_scores(
            ebitda_margin=ebitda_margin,
            growth_rate=payload.growth_rate,
            debt_to_ebitda=dte,
            revenue=payload.revenue,
            cash=payload.cash,
            debt=payload.debt,
            industry=payload.industry.value,
        )

        risk_score, risk_label, risk_breakdown, risk_factors = compute_risk_assessment(
            debt_to_ebitda=dte,
            ebitda_margin=ebitda_margin,
            growth_rate=payload.growth_rate,
            revenue=payload.revenue,
            industry=payload.industry.value,
            country=payload.country,
        )

        rec, rec_color = get_recommendation(
            revenue=payload.revenue,
            investment_score=investment_score,
            risk_score=risk_score,
        )

        response = DealScreenResponse(
            company_name=payload.company_name,
            industry=payload.industry.value,
            ebitda_margin=round(ebitda_margin, 2),
            net_debt=net_debt,
            debt_to_ebitda=round(debt_to_ebitda, 2) if debt_to_ebitda is not None else None,
            enterprise_value=valuation.enterprise_value,
            investment_score=investment_score,
            risk_score=risk_score,
            risk_label=risk_label,
            scores=scores,
            score_breakdown=score_breakdown,
            recommendation=rec,
            recommendation_color=rec_color,
            valuation=valuation,
            risk_factors=risk_factors,
            risk_breakdown=risk_breakdown,
            comps=comps_result,
        )

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
            enterprise_value=valuation.enterprise_value,
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
        raise HTTPException(status_code=500, detail=str(exc)) from exc
