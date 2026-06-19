"""
Company Intelligence API — institutional financial data gateway.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from financial_data.company_resolver import CompanyMatch, CompanyNotFoundError, search_companies
from financial_data_gateway import fetch_company_intelligence, get_provider_status
from models import (
    CompanyIntelligenceResponse,
    CompanySearchMatch,
    CompanySearchResponse,
    ProviderStatus,
)

router = APIRouter()


def _serialize_match(m: CompanyMatch) -> CompanySearchMatch:
    return CompanySearchMatch(
        ticker=m.ticker,
        company_name=m.company_name,
        exchange=m.exchange,
        match_type=m.match_type,
        confidence=round(m.confidence, 2),
        source=m.source,
    )


@router.get("/company/search", response_model=CompanySearchResponse)
def autocomplete_search(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(8, ge=1, le=20),
):
    """
    Autocomplete company search — as-you-type discovery.

    Searches local alias cache, Yahoo Finance, NASDAQ directory, and FMP (if configured).
    """
    results = search_companies(q.strip(), limit=limit)
    return CompanySearchResponse(
        query=q.strip(),
        results=[_serialize_match(m) for m in results],
    )


@router.get("/company/lookup", response_model=CompanyIntelligenceResponse)
def lookup_company(q: str = Query(..., min_length=1, max_length=100, description="Ticker or company name")):
    """
    Retrieve company fundamentals via the multi-provider financial data gateway.

    Flow: User Input → Company Resolver → Ticker → Financial Data → Analysis-ready payload.
    """
    try:
        payload = fetch_company_intelligence(q)
        return CompanyIntelligenceResponse(**payload)
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "message": str(exc),
                "suggestions": [_serialize_match(s).model_dump() for s in exc.suggestions[:8]],
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc), "suggestions": []}) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/company/providers", response_model=list[ProviderStatus])
def list_providers():
    """Enterprise Mode — show which data providers are configured."""
    return [ProviderStatus(**p) for p in get_provider_status()]
