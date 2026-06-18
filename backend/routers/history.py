"""
GET /api/history  —  Return previously screened deals from PostgreSQL.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db, ScreenedDeal

router = APIRouter()


@router.get("/history")
def get_history(
    limit: int = Query(50, ge=1, le=200),
    industry: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Return the most recent screened deals, optionally filtered by industry.
    """
    query = db.query(ScreenedDeal).order_by(ScreenedDeal.screened_at.desc())
    if industry:
        query = query.filter(ScreenedDeal.industry == industry)
    deals = query.limit(limit).all()

    return [
        {
            "id": d.id,
            "company_name": d.company_name,
            "industry": d.industry,
            "country": d.country,
            "revenue": d.revenue,
            "ebitda": d.ebitda,
            "investment_score": d.investment_score,
            "risk_score": d.risk_score,
            "recommendation": d.recommendation,
            "enterprise_value": d.enterprise_value,
            "screened_at": d.screened_at.isoformat() if d.screened_at else None,
        }
        for d in deals
    ]


@router.delete("/history/{deal_id}")
def delete_deal(deal_id: int, db: Session = Depends(get_db)):
    deal = db.query(ScreenedDeal).filter(ScreenedDeal.id == deal_id).first()
    if not deal:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Deal not found")
    db.delete(deal)
    db.commit()
    return {"message": f"Deal {deal_id} deleted"}
