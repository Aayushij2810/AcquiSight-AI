"""FactSet Research Systems provider adapter."""

from __future__ import annotations

import os
from copy import deepcopy

import httpx

from financial_data.base import BaseFinancialProvider, CompanyFinancialSnapshot, ProviderFetchResult
from financial_data.config import is_demo_mode
from financial_data.reference_data import INSTITUTIONAL_REFERENCE


class FactSetProvider(BaseFinancialProvider):
    provider_id = "factset"
    provider_label = "FactSet Research Systems"
    priority = 2
    base_confidence = "High"
    provider_quality_weight = 0.95

    def is_configured(self) -> bool:
        return bool(os.getenv("FACTSET_API_KEY")) or is_demo_mode()

    def fetch(self, ticker: str, query: str) -> ProviderFetchResult:
        if not self.is_configured():
            return self._result(None, error="FactSet API not configured")

        api_key = os.getenv("FACTSET_API_KEY")
        if api_key:
            try:
                with httpx.Client(timeout=8.0) as client:
                    resp = client.get(
                        f"https://api.factset.com/content/factset-fundamentals/v1/company/{ticker}",
                        headers={"Authorization": f"Bearer {api_key}"},
                    )
                    if resp.status_code == 200:
                        data = self._map_factset(resp.json(), ticker)
                        if data:
                            return self._result(data, confidence="High")
            except Exception:
                pass

        ref = INSTITUTIONAL_REFERENCE.get(ticker.upper())
        if ref and is_demo_mode():
            data = deepcopy(ref)
            data.raw_fields = {"source": "factset_demo_reference"}
            return self._result(data, confidence="High")

        return self._result(None, error="FactSet data unavailable")

    def _map_factset(self, payload: dict, ticker: str) -> CompanyFinancialSnapshot | None:
        try:
            f = payload.get("data", [{}])[0] if isinstance(payload.get("data"), list) else payload
            return CompanyFinancialSnapshot(
                company_name=f.get("name", ticker),
                ticker=ticker.upper(),
                industry=f.get("industry", "Other"),
                sector=f.get("sector", ""),
                country=f.get("country", "United States"),
                revenue=float(f.get("sales", 0) or 0),
                ebitda=float(f.get("ebitda", 0) or 0),
                cash=float(f.get("cash", 0) or 0),
                debt=float(f.get("debt", 0) or 0),
                market_cap=f.get("market_cap"),
                revenue_growth=float(f.get("sales_growth", 0) or 0),
                raw_fields={"factset": payload},
            )
        except (TypeError, ValueError, IndexError):
            return None
