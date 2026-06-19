"""S&P Capital IQ provider adapter."""

from __future__ import annotations

import os
from copy import deepcopy

import httpx

from financial_data.base import BaseFinancialProvider, CompanyFinancialSnapshot, ProviderFetchResult
from financial_data.config import is_demo_mode
from financial_data.reference_data import INSTITUTIONAL_REFERENCE


class CapitalIQProvider(BaseFinancialProvider):
    provider_id = "capital_iq"
    provider_label = "S&P Capital IQ"
    priority = 3
    base_confidence = "High"
    provider_quality_weight = 0.92

    def is_configured(self) -> bool:
        return bool(os.getenv("CAPITAL_IQ_API_KEY")) or is_demo_mode()

    def fetch(self, ticker: str, query: str) -> ProviderFetchResult:
        if not self.is_configured():
            return self._result(None, error="S&P Capital IQ API not configured")

        api_key = os.getenv("CAPITAL_IQ_API_KEY")
        if api_key:
            try:
                with httpx.Client(timeout=8.0) as client:
                    resp = client.get(
                        f"https://api.capitaliq.com/v1/companies/{ticker}/fundamentals",
                        headers={"X-API-Key": api_key},
                    )
                    if resp.status_code == 200:
                        data = self._map_ciq(resp.json(), ticker)
                        if data:
                            return self._result(data, confidence="High")
            except Exception:
                pass

        ref = INSTITUTIONAL_REFERENCE.get(ticker.upper())
        if ref and is_demo_mode():
            data = deepcopy(ref)
            data.comparable_companies = ref.comparable_companies or []
            data.raw_fields = {"source": "capital_iq_demo_reference"}
            return self._result(data, confidence="High")

        return self._result(None, error="Capital IQ data unavailable")

    def _map_ciq(self, payload: dict, ticker: str) -> CompanyFinancialSnapshot | None:
        try:
            return CompanyFinancialSnapshot(
                company_name=payload.get("companyName", ticker),
                ticker=ticker.upper(),
                industry=payload.get("industry", "Other"),
                sector=payload.get("sector", ""),
                country=payload.get("country", "United States"),
                revenue=float(payload.get("totalRevenue", 0) or 0),
                ebitda=float(payload.get("ebitda", 0) or 0),
                market_cap=payload.get("marketCap"),
                enterprise_value=payload.get("enterpriseValue"),
                ev_ebitda_multiple=payload.get("evToEbitda"),
                raw_fields={"capital_iq": payload},
            )
        except (TypeError, ValueError):
            return None
