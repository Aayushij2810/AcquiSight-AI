"""AcquiSight Copilot — grounded investment Q&A."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from copilot_engine import run_copilot
from database import InvestmentOpportunity, get_db
from models import CopilotChatRequest, CopilotChatResponse, CopilotSourceMetric

router = APIRouter()


@router.post("/copilot/chat", response_model=CopilotChatResponse)
async def copilot_chat(payload: CopilotChatRequest, db: Session = Depends(get_db)):
    opportunities = (
        db.query(InvestmentOpportunity)
        .order_by(InvestmentOpportunity.priority_score.desc())
        .all()
    )
    result = await run_copilot(payload.message, opportunities)
    return CopilotChatResponse(
        answer=result["answer"],
        intent=result["intent"],
        companies=result["companies"],
        sources=[CopilotSourceMetric(**s) for s in result["sources"]],
        grounded_in=result["grounded_in"],
    )
