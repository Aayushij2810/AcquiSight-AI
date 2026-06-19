"""Yahoo Finance final fallback provider — global public company coverage."""

from __future__ import annotations

from financial_data.base import BaseFinancialProvider, ProviderFetchResult
from financial_data.yahoo_client import fetch_company_snapshot


class YahooProvider(BaseFinancialProvider):
    provider_id = "yahoo"
    provider_label = "Yahoo Finance"
    priority = 5
    base_confidence = "Medium"
    provider_quality_weight = 0.65
    credential_env_var = None

    def has_credentials(self) -> bool:
        return True

    def fetch(self, ticker: str, query: str) -> ProviderFetchResult:
        try:
            data = fetch_company_snapshot(ticker, query)
            if not data:
                return self._result(None, error="Symbol not found on Yahoo Finance")
            conf = "Medium" if data.revenue > 0 else "Low"
            return self._result(data, confidence=conf)
        except Exception as exc:
            err = str(exc)
            if any(x in err for x in ("Too Many Requests", "429", "Expecting value")):
                return self._result(None, error="Yahoo Finance temporarily unavailable")
            return self._result(None, error=err)
