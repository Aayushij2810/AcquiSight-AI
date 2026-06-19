"""AcquiSight AI — FastAPI entry-point."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from scoring       import calculate_scores, get_recommendation
from valuation     import calculate_enterprise_value, calculate_financial_ratios
from risk          import calculate_risk_score
from comps         import get_comparable_companies
from memo_generator import generate_investment_memo

# ── app ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AcquiSight AI",
    description="AI-Powered Private Equity Deal Screening API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── schemas ──────────────────────────────────────────────────────────────────
class DealInput(BaseModel):
    company_name: str  = Field(..., example="Acme Cloud Software")
    industry:     str  = Field(..., example="SaaS")
    revenue:      float = Field(..., gt=0, example=85_000_000)
    ebitda:       float = Field(...,       example=22_000_000)
    growth_rate:  float = Field(...,       example=28.0)
    debt:         float = Field(0.0,       example=45_000_000)
    cash:         float = Field(0.0,       example=12_000_000)
    country:      str  = Field("US",       example="United States")


class MemoRequest(BaseModel):
    screen_result: dict
    analyst_notes: Optional[str] = None


# ── in-memory history (replace with Postgres via SQLAlchemy in production) ───
_history: list[dict] = []


# ── routes ───────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/screen")
def screen_deal(inp: DealInput):
    try:
        ratios = calculate_financial_ratios(inp.revenue, inp.ebitda, inp.debt, inp.cash)
        ev     = calculate_enterprise_value(inp.ebitda, inp.industry)
        scores = calculate_scores(
            revenue=inp.revenue, ebitda=inp.ebitda, growth_rate=inp.growth_rate,
            debt=inp.debt, cash=inp.cash, industry=inp.industry,
        )
        risk   = calculate_risk_score(
            ebitda_margin=ratios["ebitda_margin"],
            debt_to_ebitda=ratios["debt_to_ebitda"],
            growth_rate=inp.growth_rate,
            investment_score=scores["investment_score"],
        )
        comps  = get_comparable_companies(inp.industry, inp.ebitda)
        rec    = get_recommendation(scores["investment_score"], risk["risk_score"])

        result = {
            "company_name":         inp.company_name,
            "industry":             inp.industry,
            "ebitda_margin":        ratios["ebitda_margin"],
            "net_debt":             ratios["net_debt"],
            "debt_to_ebitda":       ratios["debt_to_ebitda"],
            "enterprise_value":     ev["enterprise_value"],
            "investment_score":     scores["investment_score"],
            "risk_score":           risk["risk_score"],
            "scores":               scores["dimensions"],
            "recommendation":       rec["recommendation"],
            "recommendation_color": rec["color"],
            "comps":                comps,
        }
        _history.append(result)
        return result

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/memo")
def get_memo(req: MemoRequest):
    try:
        return generate_investment_memo(req.screen_result, req.analyst_notes)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/history")
def get_history():
    return _history[-50:]
