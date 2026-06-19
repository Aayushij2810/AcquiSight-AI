"""Financial Modeling Prep fallback provider."""

from __future__ import annotations

import os

import httpx

from financial_data.base import BaseFinancialProvider, CompanyFinancialSnapshot, ProviderFetchResult
from financial_data.industry_map import map_industry


class FMPProvider(BaseFinancialProvider):
    provider_id = "fmp"
    provider_label = "Financial Modeling Prep"
    priority = 4
    base_confidence = "Medium"
    provider_quality_weight = 0.78
    credential_env_var = "FMP_API_KEY"

    def has_credentials(self) -> bool:
        return bool(os.getenv("FMP_API_KEY"))

    def fetch(self, ticker: str, query: str) -> ProviderFetchResult:
        api_key = os.getenv("FMP_API_KEY")
        if not api_key:
            return self._result(None, error="FMP_API_KEY not set")

        try:
            with httpx.Client(timeout=10.0) as client:
                profile = client.get(
                    f"https://financialmodelingprep.com/api/v3/profile/{ticker.upper()}",
                    params={"apikey": api_key},
                ).json()
                metrics = client.get(
                    f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker.upper()}",
                    params={"apikey": api_key},
                ).json()
                income = client.get(
                    f"https://financialmodelingprep.com/api/v3/income-statement/{ticker.upper()}",
                    params={"apikey": api_key, "limit": 2},
                ).json()

            if not profile or not isinstance(profile, list):
                return self._result(None, error="FMP profile not found")

            p = profile[0]
            m = metrics[0] if metrics else {}
            rev = float(income[0].get("revenue", 0) if income else 0)
            ebitda = float(income[0].get("ebitda", 0) if income else 0)
            prev_rev = float(income[1].get("revenue", 0)) if income and len(income) > 1 else 0
            growth = ((rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0.0
            margin = (ebitda / rev * 100) if rev > 0 else 0.0

            data = CompanyFinancialSnapshot(
                company_name=p.get("companyName", ticker),
                ticker=ticker.upper(),
                industry=map_industry(p.get("sector", ""), p.get("industry", "")),
                sector=p.get("sector", "") or "",
                country=p.get("country", "United States") or "United States",
                revenue=rev,
                ebitda=ebitda,
                net_income=float(income[0].get("netIncome", 0)) if income else None,
                cash=float(m.get("cashAndCashEquivalents", 0) or 0),
                debt=float(m.get("totalDebt", 0) or 0),
                market_cap=float(p.get("mktCap", 0) or 0) or None,
                enterprise_value=float(m.get("enterpriseValue", 0) or 0) or None,
                revenue_growth=round(growth, 2),
                ebitda_margin=round(margin, 2),
                ev_ebitda_multiple=float(m.get("enterpriseValueOverEBITDA", 0) or 0) or None,
                historical_financials=[
                    {"period": row.get("date"), "revenue": row.get("revenue"), "ebitda": row.get("ebitda")}
                    for row in (income or [])[:4]
                ],
                raw_fields={"fmp_profile": p, "fmp_metrics": m},
            )
            return self._result(data, confidence="Medium")
        except Exception as exc:
            return self._result(None, error=str(exc))
