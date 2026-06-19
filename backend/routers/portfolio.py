"""
Portfolio Mode API — deal pipeline, analytics, insights, export.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import InvestmentOpportunity, get_db
from models import (
    AddToPortfolioRequest,
    ICDecision,
    PipelineStatus,
    PortfolioInsightsResponse,
    PortfolioOpportunity,
    PortfolioUpdateRequest,
)
from portfolio import PIPELINE_STAGES, build_analytics, compute_priority_score, opportunity_to_dict
from portfolio_insights import generate_portfolio_insights

router = APIRouter()


def _get_all(db: Session) -> list[InvestmentOpportunity]:
    return db.query(InvestmentOpportunity).order_by(
        InvestmentOpportunity.priority_score.desc(),
        InvestmentOpportunity.date_added.desc(),
    ).all()


@router.post("/portfolio", response_model=PortfolioOpportunity)
def add_to_portfolio(payload: AddToPortfolioRequest, db: Session = Depends(get_db)):
    s = payload.screen_result
    existing = (
        db.query(InvestmentOpportunity)
        .filter(InvestmentOpportunity.company_name == s.company_name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail=f"{s.company_name} is already in the portfolio.")

    priority = compute_priority_score(s.investment_score, s.risk_score)
    timing = s.timing
    opp = InvestmentOpportunity(
        company_name=s.company_name,
        industry=s.industry,
        revenue=payload.revenue,
        ebitda=payload.ebitda,
        growth_rate=payload.growth_rate,
        debt=payload.debt,
        cash=payload.cash,
        investment_score=s.investment_score,
        risk_score=s.risk_score,
        recommendation=s.recommendation,
        enterprise_value=s.enterprise_value,
        priority_score=priority,
        status=payload.status.value,
        notes=payload.notes or "",
        watchlist=payload.watchlist,
        ic_decision=ICDecision.PENDING.value,
        screen_result_json=s.model_dump(),
        memo_json=payload.memo.model_dump() if payload.memo else None,
        timing_score=timing.timing_score,
        best_quarter=timing.best_quarter,
        timing_confidence=timing.confidence_level,
        entry_assessment=timing.entry_window_assessment,
        timing_json=timing.model_dump(),
    )
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return PortfolioOpportunity(**opportunity_to_dict(opp))


@router.get("/portfolio", response_model=list[PortfolioOpportunity])
def list_portfolio(
    status: str | None = Query(None),
    industry: str | None = Query(None),
    watchlist: bool | None = Query(None),
    sort_by: str = Query("priority_score"),
    db: Session = Depends(get_db),
):
    query = db.query(InvestmentOpportunity)
    if status:
        query = query.filter(InvestmentOpportunity.status == status)
    if industry:
        query = query.filter(InvestmentOpportunity.industry == industry)
    if watchlist is not None:
        query = query.filter(InvestmentOpportunity.watchlist == watchlist)

    sort_map = {
        "priority_score": InvestmentOpportunity.priority_score.desc(),
        "investment_score": InvestmentOpportunity.investment_score.desc(),
        "risk_score": InvestmentOpportunity.risk_score.asc(),
        "enterprise_value": InvestmentOpportunity.enterprise_value.desc(),
        "growth_rate": InvestmentOpportunity.growth_rate.desc(),
        "date_added": InvestmentOpportunity.date_added.desc(),
        "timing_score": InvestmentOpportunity.timing_score.desc(),
    }
    query = query.order_by(sort_map.get(sort_by, InvestmentOpportunity.priority_score.desc()))
    return [PortfolioOpportunity(**opportunity_to_dict(o)) for o in query.all()]


@router.get("/portfolio/analytics")
def portfolio_analytics(db: Session = Depends(get_db)):
    return build_analytics(_get_all(db))


@router.get("/portfolio/stages")
def pipeline_stages():
    return {"stages": PIPELINE_STAGES}


@router.post("/portfolio/insights", response_model=PortfolioInsightsResponse)
async def portfolio_insights(db: Session = Depends(get_db)):
    opps = _get_all(db)
    summary, recs = await generate_portfolio_insights(opps)
    return PortfolioInsightsResponse(
        summary=summary,
        recommendations=recs,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/portfolio/export/csv")
def export_csv(db: Session = Depends(get_db)):
    opps = _get_all(db)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Company", "Industry", "Investment Score", "Risk Score", "Timing Score",
        "Best Quarter", "Confidence", "Entry Assessment", "Priority Score",
        "Enterprise Value", "Growth Rate", "Recommendation", "Status", "IC Decision",
        "Watchlist", "Date Added", "Notes",
    ])
    for i, o in enumerate(opps, 1):
        writer.writerow([
            i, o.company_name, o.industry, o.investment_score, o.risk_score,
            o.timing_score or "", o.best_quarter or "", o.timing_confidence or "",
            o.entry_assessment or "", o.priority_score, o.enterprise_value, o.growth_rate,
            o.recommendation, o.status, o.ic_decision, o.watchlist,
            o.date_added.isoformat() if o.date_added else "", o.notes or "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=acquisight_pipeline.csv"},
    )


@router.get("/portfolio/{opp_id}", response_model=PortfolioOpportunity)
def get_opportunity(opp_id: int, db: Session = Depends(get_db)):
    opp = db.query(InvestmentOpportunity).filter(InvestmentOpportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return PortfolioOpportunity(**opportunity_to_dict(opp))


@router.patch("/portfolio/{opp_id}", response_model=PortfolioOpportunity)
def update_opportunity(opp_id: int, payload: PortfolioUpdateRequest, db: Session = Depends(get_db)):
    opp = db.query(InvestmentOpportunity).filter(InvestmentOpportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    if payload.status is not None:
        opp.status = payload.status.value
    if payload.notes is not None:
        opp.notes = payload.notes
    if payload.watchlist is not None:
        opp.watchlist = payload.watchlist
    if payload.ic_decision is not None:
        opp.ic_decision = payload.ic_decision.value
        if payload.ic_decision == ICDecision.APPROVED:
            opp.status = PipelineStatus.APPROVED.value
        elif payload.ic_decision == ICDecision.REJECTED:
            opp.status = PipelineStatus.REJECTED.value

    db.commit()
    db.refresh(opp)
    return PortfolioOpportunity(**opportunity_to_dict(opp))


@router.delete("/portfolio/{opp_id}")
def delete_opportunity(opp_id: int, db: Session = Depends(get_db)):
    opp = db.query(InvestmentOpportunity).filter(InvestmentOpportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    db.delete(opp)
    db.commit()
    return {"message": f"Opportunity {opp_id} removed from portfolio"}
