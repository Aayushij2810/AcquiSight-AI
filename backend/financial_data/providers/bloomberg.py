"""Bloomberg Professional Data provider adapter."""

from __future__ import annotations

import os
from copy import deepcopy

import httpx

from financial_data.base import BaseFinancialProvider, CompanyFinancialSnapshot, ProviderFetchResult
from financial_data.config import is_demo_mode
from financial_data.reference_data import INSTITUTIONAL_REFERENCE


class BloombergProvider(BaseFinancialProvider):
    """
    Enterprise adapter for Bloomberg API (B-PIPE / REST).

    Configure via:
      BLOOMBERG_API_KEY
      BLOOMBERG_API_URL  (optional custom endpoint)
      INSTITUTIONAL_DEMO_MODE=1  (serves reference data for demo tickers)
    """

    provider_id = "bloomberg"
    provider_label = "Bloomberg Professional Data"
    priority = 1
    base_confidence = "High"
    provider_quality_weight = 1.0

    def is_configured(self) -> bool:
        return bool(os.getenv("BLOOMBERG_API_KEY")) or is_demo_mode()

    def fetch(self, ticker: str, query: str) -> ProviderFetchResult:
        if not self.is_configured():
            return self._result(None, error="Bloomberg API not configured")

        api_key = os.getenv("BLOOMBERG_API_KEY")
        api_url = os.getenv("BLOOMBERG_API_URL", "https://api.bloomberg.com/eap/catalogs")

        if api_key:
            try:
                # Production integration point — map Bloomberg field mnemonics to snapshot.
                with httpx.Client(timeout=8.0) as client:
                    resp = client.get(
                        f"{api_url}/company/{ticker}/fundamentals",
                        headers={"Authorization": f"Bearer {api_key}"},
                    )
                    if resp.status_code == 200:
                        payload = resp.json()
                        data = self._map_bloomberg_payload(ticker, payload)
                        if data:
                            return self._result(data, confidence="High")
            except Exception as exc:
                pass  # fall through to demo reference

        ref = INSTITUTIONAL_REFERENCE.get(ticker.upper())
        if ref and is_demo_mode():
            data = deepcopy(ref)
            data.raw_fields = {"source": "bloomberg_demo_reference", "query": query}
            return self._result(data, confidence="High")

        return self._result(None, error="Bloomberg data unavailable for this symbol")

    def _map_bloomberg_payload(self, ticker: str, payload: dict) -> CompanyFinancialSnapshot | None:
        """Map Bloomberg REST payload to normalized snapshot."""
        try:
            return CompanyFinancialSnapshot(
                company_name=payload.get("name", ticker),
                ticker=ticker.upper(),
                industry=payload.get("industry", "Other"),
                sector=payload.get("sector", ""),
                country=payload.get("country", "United States"),
                revenue=float(payload.get("revenue", 0)),
                ebitda=float(payload.get("ebitda", 0)),
                net_income=payload.get("net_income"),
                cash=float(payload.get("cash", 0)),
                debt=float(payload.get("debt", 0)),
                market_cap=payload.get("market_cap"),
                enterprise_value=payload.get("enterprise_value"),
                revenue_growth=float(payload.get("revenue_growth", 0)),
                ebitda_margin=float(payload.get("ebitda_margin", 0)),
                raw_fields={"bloomberg": payload},
            )
        except (TypeError, ValueError):
            return None
