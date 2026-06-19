"""
AcquiSight AI — Financial Data Gateway

Unified entry point for institutional financial data.
Automatically selects the highest-priority available provider and
cross-validates across secondary sources when available.

Priority:
  1. Bloomberg
  2. FactSet
  3. S&P Capital IQ
  4. Financial Modeling Prep
  5. Yahoo Finance
"""

from __future__ import annotations

from datetime import datetime, timezone

from financial_data.config import ensure_env
from financial_data.base import ProviderFetchResult

ensure_env()
from financial_data.company_resolver import CompanyMatch, CompanyNotFoundError, resolve_company
from financial_data.cross_validation import CrossValidationResult, cross_validate
from financial_data.providers import (
    BloombergProvider,
    CapitalIQProvider,
    FactSetProvider,
    FMPProvider,
    YahooProvider,
)
from financial_data.config import is_demo_mode
from financial_data.reference_data import INSTITUTIONAL_REFERENCE
from financial_data.reliability import compute_reliability_score


def _should_query_provider(provider, ticker: str) -> bool:
    """Skip demo enterprise providers when reference data is unavailable for this ticker."""
    if provider.provider_id in ("yahoo",):
        return True
    if provider.provider_id == "fmp":
        return provider.is_configured()
    if not provider.is_configured():
        return False
    if is_demo_mode() and ticker.upper() not in INSTITUTIONAL_REFERENCE:
        import os
        key_map = {
            "bloomberg": "BLOOMBERG_API_KEY",
            "factset": "FACTSET_API_KEY",
            "capital_iq": "CAPITAL_IQ_API_KEY",
        }
        if not os.getenv(key_map.get(provider.provider_id, "")):
            return False
    return True


PROVIDERS = [
    BloombergProvider(),
    FactSetProvider(),
    CapitalIQProvider(),
    FMPProvider(),
    YahooProvider(),
]


def get_provider_status() -> list[dict]:
    """Return configuration status for all providers (Enterprise Mode dashboard)."""
    return [
        {
            "provider_id": p.provider_id,
            "provider_label": p.provider_label,
            "priority": p.priority,
            "configured": p.is_configured(),
            "quality_weight": p.provider_quality_weight,
        }
        for p in PROVIDERS
    ]


def fetch_company_intelligence(query: str) -> dict:
    """
    Retrieve company intelligence through the multi-provider gateway.

    User Input → Company Resolver → Ticker → Financial Data → Response
    """
    resolution = resolve_company(query)
    if not resolution.match:
        raise CompanyNotFoundError(
            f"Unable to find company '{query}'.",
            suggestions=resolution.suggestions,
        )

    tickers_to_try = [resolution.match.ticker]
    tickers_to_try.extend(s.ticker for s in resolution.suggestions[:3] if s.ticker not in tickers_to_try)

    last_error = ""
    for ticker in tickers_to_try:
        try:
            return _build_intelligence_response(query, ticker, resolution.match)
        except ValueError as exc:
            last_error = str(exc)

    raise CompanyNotFoundError(
        last_error or f"No financial data found for '{query}'.",
        suggestions=resolution.suggestions,
    )


def _build_intelligence_response(query: str, ticker: str, resolved: CompanyMatch) -> dict:
    results: list[ProviderFetchResult] = []

    for provider in PROVIDERS:
        if _should_query_provider(provider, ticker):
            results.append(provider.fetch(ticker, query))

    successful = [r for r in results if r.data]
    if not successful:
        errors = [f"{r.provider_label}: {r.error}" for r in results if r.error]
        raise ValueError(
            f"No financial data found for '{query}' ({ticker}). "
            + ("; ".join(errors) if errors else "All providers unavailable.")
        )

    successful.sort(key=lambda r: r.priority)
    primary = successful[0]

    cv = cross_validate(results)
    reliability_score, reliability_grade, confidence = compute_reliability_score(
        primary, results, cv.flagged if cv else False,
    )

    display_confidence = confidence if reliability_score >= 75 else primary.confidence
    data = primary.data
    assert data is not None

    fiscal_period = None
    if data.raw_fields:
        fiscal_period = data.raw_fields.get("fiscal_period")

    fallback_chain = [r.provider_label for r in results if r.error and not r.data]
    now = datetime.now(timezone.utc).isoformat()

    return {
        "query": query,
        "ticker": data.ticker,
        "company_name": (
            resolved.company_name
            if data.company_name.upper() == data.ticker.upper()
            else (data.company_name or resolved.company_name)
        ),
        "industry": data.industry,
        "sector": data.sector,
        "country": data.country,
        "revenue": data.revenue,
        "ebitda": data.ebitda,
        "net_income": data.net_income,
        "cash": data.cash,
        "debt": data.debt,
        "market_cap": data.market_cap,
        "enterprise_value": data.enterprise_value,
        "revenue_growth": data.revenue_growth,
        "ebitda_margin": data.ebitda_margin,
        "ev_ebitda_multiple": data.ev_ebitda_multiple,
        "historical_financials": data.historical_financials,
        "earnings_dates": data.earnings_dates,
        "consensus_estimates": data.consensus_estimates,
        "comparable_companies": data.comparable_companies,
        "provenance": {
            "data_source": primary.provider_label,
            "provider_id": primary.provider_id,
            "last_updated": now,
            "confidence": display_confidence,
            "reliability_score": reliability_score,
            "reliability_grade": reliability_grade,
            "fallback_chain": fallback_chain,
            "fiscal_period": fiscal_period,
            "data_freshness": "Live market data",
        },
        "resolution": {
            "match_type": resolved.match_type,
            "confidence": round(resolved.confidence, 2),
            "source": resolved.source,
            "resolved_ticker": resolved.ticker,
            "resolved_name": resolved.company_name,
        },
        "cross_validation": _serialize_cv(cv),
        "providers_attempted": [
            {
                "provider_id": r.provider_id,
                "provider_label": r.provider_label,
                "success": r.data is not None,
                "error": r.error,
                "confidence": r.confidence if r.data else None,
            }
            for r in results
        ],
        "provider_status": get_provider_status(),
    }


def _serialize_cv(cv: CrossValidationResult | None) -> dict | None:
    if not cv:
        return None
    return {
        "flagged": cv.flagged,
        "message": cv.message,
        "providers_compared": cv.providers_compared,
        "discrepancies": [
            {
                "field": d.field,
                "values": d.values,
                "max_difference_pct": d.max_difference_pct,
            }
            for d in cv.discrepancies
        ],
    }
