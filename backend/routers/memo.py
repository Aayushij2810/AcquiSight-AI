"""
POST /api/memo  —  AI investment memo generation.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from models import MemoRequest, MemoResponse
from memo_generator import generate_memo

router = APIRouter()


@router.post("/memo", response_model=MemoResponse)
async def create_memo(payload: MemoRequest):
    """
    Generate a professional PE-style investment memo using GPT-4o.
    Returns structured sections suitable for rendering or PDF export.
    """
    try:
        memo = await generate_memo(
            screen_result=payload.screen_result,
            analyst_notes=payload.analyst_notes,
        )
        return memo
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Memo generation failed: {exc}")
