"""Bloomberg Professional Data provider adapter."""

from __future__ import annotations

import os

import httpx

from financial_data.base import BaseFinancialProvider, CompanyFinancialSnapshot, ProviderFetchResult


class BloombergProvider(BaseFinancialProvider):
    """
    Enterprise adapter for Bloomberg API (B-PIPE / REST).

    Requires BLOOMBERG_API_KEY — never serves data without valid credentials.
    """

    provider_id = "bloomberg"
    provider_label = "Bloomberg"
    priority = 1
    base_confidence = "High"
    provider_quality_weight = 1.0
    credential_env_var = "BLOOMBERG_API_KEY"

    def has_credentials(self) -> bool:
        return bool(os.getenv("BLOOMBERG_API_KEY"))

    def fetch(self, ticker: str, query: str) -> ProviderFetchResult:
        if not self.has_credentials():
            return self._result(None, error="Bloomberg API credentials not configured")

        api_key = os.getenv("BLOOMBERG_API_KEY")
        api_url = os.getenv("BLOOMBERG_API_URL", "https://api.bloomberg.com/eap/catalogs")

        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(
                    f"{api_url}/company/{ticker}/fundamentals",
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                if resp.status_code == 200:
                    data = self._map_bloomberg_payload(ticker, resp.json())
                    if data:
                        return self._result(data, confidence="High")
        except Exception:
            pass

        return self._result(None, error="Bloomberg data unavailable for this symbol")

    def _map_bloomberg_payload(self, ticker: str, payload: dict) -> CompanyFinancialSnapshot | None:
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
