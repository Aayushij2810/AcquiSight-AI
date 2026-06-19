"""Reporting currency resolution for international listings."""

from __future__ import annotations

import os
from typing import Optional

import httpx

FMP_STABLE = "https://financialmodelingprep.com/stable"

# Yahoo / exchange suffix → ISO 4217 (fallback when profile lookup fails).
_SUFFIX_CURRENCIES: dict[str, str] = {
    "NS": "INR",
    "BO": "INR",
    "L": "GBP",
    "IL": "GBP",
    "TO": "CAD",
    "V": "CAD",
    "KS": "KRW",
    "KQ": "KRW",
    "T": "JPY",
    "HK": "HKD",
    "SS": "CNY",
    "SZ": "CNY",
    "AX": "AUD",
    "NZ": "NZD",
    "SW": "CHF",
    "SA": "BRL",
    "MX": "MXN",
    "SI": "SGD",
    "TW": "TWD",
}


def currency_from_ticker_suffix(ticker: str) -> str:
    sym = ticker.upper()
    if "." in sym:
        suffix = sym.rsplit(".", 1)[-1]
        if suffix in _SUFFIX_CURRENCIES:
            return _SUFFIX_CURRENCIES[suffix]
    return "USD"


def _fetch_fmp_currency(ticker: str) -> Optional[str]:
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        return None
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(
                f"{FMP_STABLE}/profile",
                params={"symbol": ticker.upper(), "apikey": api_key},
            )
            if resp.status_code != 200:
                return None
            rows = resp.json()
            if not isinstance(rows, list) or not rows:
                return None
            currency = rows[0].get("currency")
            if isinstance(currency, str) and len(currency) == 3:
                return currency.upper()
    except Exception:
        return None
    return None


def _fetch_yahoo_currency(ticker: str) -> Optional[str]:
    try:
        from yahooquery import Ticker

        sym = ticker.upper()
        t = Ticker(sym)
        for source in (t.price, t.summary_detail):
            payload = source.get(sym) if source else None
            if not isinstance(payload, dict):
                continue
            currency = payload.get("currency")
            if isinstance(currency, str) and len(currency) == 3:
                return currency.upper()
    except Exception:
        return None
    return None


def resolve_reporting_currency(ticker: str) -> str:
    """Best-effort ISO currency for a listed symbol's financials and prices."""
    for resolver in (_fetch_fmp_currency, _fetch_yahoo_currency, currency_from_ticker_suffix):
        currency = resolver(ticker)
        if currency:
            return currency
    return "USD"
