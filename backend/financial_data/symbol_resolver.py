"""Resolve company name or ticker — delegates to Company Resolution Engine."""

from financial_data.company_resolver import (
    CompanyMatch,
    CompanyNotFoundError,
    ResolutionResult,
    resolve_company,
    resolve_ticker,
    search_companies,
)

__all__ = [
    "CompanyMatch",
    "CompanyNotFoundError",
    "ResolutionResult",
    "resolve_company",
    "resolve_ticker",
    "search_companies",
]
