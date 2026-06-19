"""Abstract financial data provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class CompanyFinancialSnapshot:
    """Normalized company financial snapshot from any provider."""

    company_name: str
    ticker: str
    industry: str
    sector: str
    country: str
    revenue: float
    ebitda: float
    net_income: Optional[float] = None
    cash: float = 0.0
    debt: float = 0.0
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    revenue_growth: float = 0.0
    ebitda_margin: float = 0.0
    ev_ebitda_multiple: Optional[float] = None
    historical_financials: list[dict[str, Any]] = field(default_factory=list)
    earnings_dates: list[str] = field(default_factory=list)
    consensus_estimates: dict[str, Any] = field(default_factory=dict)
    comparable_companies: list[str] = field(default_factory=list)
    raw_fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderFetchResult:
    provider_id: str
    provider_label: str
    priority: int
    available: bool
    provider_quality_weight: float = 0.65
    data: Optional[CompanyFinancialSnapshot] = None
    error: Optional[str] = None
    confidence: str = "Low"
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    fields_populated: int = 0


class BaseFinancialProvider(ABC):
    """All institutional data providers implement this interface."""

    provider_id: str
    provider_label: str
    priority: int
    base_confidence: str = "Medium"
    provider_quality_weight: float = 0.75

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True when API credentials or demo mode enables this provider."""

    @abstractmethod
    def fetch(self, ticker: str, query: str) -> ProviderFetchResult:
        """Fetch normalized financial snapshot for ticker."""

    def _result(
        self,
        data: Optional[CompanyFinancialSnapshot],
        error: Optional[str] = None,
        confidence: Optional[str] = None,
    ) -> ProviderFetchResult:
        fields = 0
        if data:
            for attr in (
                "revenue", "ebitda", "cash", "debt", "market_cap",
                "enterprise_value", "revenue_growth", "ebitda_margin",
            ):
                val = getattr(data, attr, None)
                if val is not None and val != 0:
                    fields += 1
        return ProviderFetchResult(
            provider_id=self.provider_id,
            provider_label=self.provider_label,
            priority=self.priority,
            available=self.is_configured(),
            provider_quality_weight=self.provider_quality_weight,
            data=data,
            error=error,
            confidence=confidence or self.base_confidence,
            fields_populated=fields,
        )
