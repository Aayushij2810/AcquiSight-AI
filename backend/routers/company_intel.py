"""
Company Intelligence API — institutional financial data gateway.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from financial_data.company_resolver import CompanyMatch, CompanyNotFoundError, search_companies
from financial_data_gateway import (
    fetch_company_intelligence,
    get_data_layer_dashboard,
    get_provider_status,
)
from historical_trends import fetch_historical_trends
from models import (
    CompanyIntelligenceResponse,
    CompanySearchMatch,
    CompanySearchResponse,
    DataLayerStatusResponse,
    HistoricalTrendsResponse,
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
    """Autocomplete company search — as-you-type discovery."""
    results = search_companies(q.strip(), limit=limit)
    return CompanySearchResponse(
        query=q.strip(),
        results=[_serialize_match(m) for m in results],
    )


@router.get("/company/lookup", response_model=CompanyIntelligenceResponse)
def lookup_company(q: str = Query(..., min_length=1, max_length=100, description="Ticker or company name")):
    """Retrieve company fundamentals via the multi-provider financial data gateway."""
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


@router.get("/company/historical-trends", response_model=HistoricalTrendsResponse)
def historical_trends(q: str = Query(..., min_length=1, max_length=100)):
    """5-year revenue, EBITDA, growth, and share price trends."""
    try:
        return HistoricalTrendsResponse(**fetch_historical_trends(q))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/company/data-layer/status", response_model=DataLayerStatusResponse)
def data_layer_status():
    """Honest data-layer connection dashboard for Settings."""
    return DataLayerStatusResponse(**get_data_layer_dashboard())


@router.get("/company/providers", response_model=list[ProviderStatus])
def list_providers():
    """Legacy provider list — configured reflects actual credentials only."""
    return [
        ProviderStatus(
            provider_id=p["provider_id"],
            provider_label=p["provider_label"],
            priority=p["priority"],
            configured=p["connection_state"] == "connected",
            quality_weight=p["quality_weight"],
        )
        for p in get_provider_status()
    ]
