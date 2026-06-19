"""
Historical Financial Trends — 5-year revenue, EBITDA, growth, and share price.

Data sources (priority):
  1. Financial Modeling Prep (stable API)
  2. Yahoo Finance fallback
"""

from __future__ import annotations

import math
import os
import statistics
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from financial_data.company_resolver import resolve_company
from financial_data.config import ensure_env
from financial_data.currency import resolve_reporting_currency

ensure_env()

FMP_STABLE = "https://financialmodelingprep.com/stable"
_YEARS = 5


def _listing_variants(ticker: str) -> list[str]:
    """Try primary ticker plus common international exchange suffixes."""
    sym = ticker.upper()
    variants = [sym]
    if "." not in sym:
        base = sym
        for suffix in (".NS", ".BO", ".L", ".TO"):
            variants.append(f"{base}{suffix}")
    return variants


def fetch_historical_trends(query: str) -> dict:
    """Retrieve 5-year historical trends for a public company."""
    resolution = resolve_company(query)
    if not resolution.match:
        raise ValueError(f"Unable to resolve company: {query}")

    ticker = resolution.match.ticker
    company_name = resolution.match.company_name

    years = None
    data_ticker = ticker
    fmp_rows: list[dict] = []
    yahoo_rows: list[dict] = []
    price_by_year: dict[int, float] = {}

    best_valid_count = 0
    best_fmp_rows: list[dict] = []
    best_yahoo_rows: list[dict] = []
    for sym in _listing_variants(ticker):
        fmp_rows = _fetch_fmp_financials(sym)
        yahoo_rows = _fetch_yahoo_financials(sym)
        merged = _merge_financial_rows(fmp_rows, yahoo_rows)
        fmp_prices = _fetch_fmp_prices(sym)
        yahoo_prices = _fetch_yahoo_prices(sym)
        prices = {**yahoo_prices, **fmp_prices}
        candidate_years = _build_year_series(merged, prices)
        valid_count = sum(
            1 for y in candidate_years
            if y.get("revenue") is not None or y.get("ebitda") is not None
        )
        if valid_count >= 2 and valid_count > best_valid_count:
            data_ticker = sym
            years = candidate_years
            price_by_year = prices
            best_fmp_rows = fmp_rows
            best_yahoo_rows = yahoo_rows
            best_valid_count = valid_count

    if not years:
        raise ValueError(f"Insufficient historical data for {ticker}.")

    years = [y for y in years if y.get("revenue") is not None or y.get("ebitda") is not None]
    if len(years) < 2:
        raise ValueError(f"Insufficient historical data for {ticker}.")

    # Keep the most recent N fiscal years (prefer longer history when Yahoo extends FMP).
    years = years[-min(len(years), _YEARS + 1):][-_YEARS:] if len(years) > _YEARS else years
    _attach_growth_rates(years)

    source = "Financial Modeling Prep" if best_fmp_rows else "Yahoo Finance"
    if best_fmp_rows and best_yahoo_rows:
        source = "Financial Modeling Prep + Yahoo Finance"

    metrics = _compute_metrics(years)
    period_label = f"{years[0]['label']} → {years[-1]['label']}"
    currency = resolve_reporting_currency(data_ticker)

    return {
        "query": query,
        "ticker": data_ticker,
        "company_name": company_name,
        "currency": currency,
        "data_source": source,
        "period_label": period_label,
        "years": years,
        "metrics": metrics,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


def _fetch_fmp_financials(ticker: str) -> list[dict]:
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        return []
    try:
        with httpx.Client(timeout=12.0) as client:
            resp = client.get(
                f"{FMP_STABLE}/income-statement",
                params={"symbol": ticker.upper(), "period": "annual", "limit": _YEARS, "apikey": api_key},
            )
            if resp.status_code != 200:
                return []
            rows = resp.json()
            if not isinstance(rows, list):
                return []
            return [
                {
                    "date": r.get("date"),
                    "year": _year_from_date(r.get("date")),
                    "revenue": _float(r.get("revenue")),
                    "ebitda": _float(r.get("ebitda")),
                    "source": "fmp",
                }
                for r in rows
                if r.get("date")
            ]
    except Exception:
        return []


def _fetch_fmp_prices(ticker: str) -> dict[int, float]:
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        return {}
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(
                f"{FMP_STABLE}/historical-price-eod/full",
                params={"symbol": ticker.upper(), "from": "2018-01-01", "apikey": api_key},
            )
            if resp.status_code != 200:
                return {}
            rows = resp.json()
            if not isinstance(rows, list):
                return {}
            return _year_end_closes(rows, date_key="date", price_key="close")
    except Exception:
        return {}


def _fetch_yahoo_financials(ticker: str) -> list[dict]:
    try:
        from yahooquery import Ticker

        t = Ticker(ticker.upper())
        inc = t.income_statement(frequency="a")
        if inc is None or getattr(inc, "empty", True):
            return []

        subset = inc.loc[ticker.upper()] if ticker.upper() in inc.index else inc
        rows: list[dict] = []
        seen: set[int] = set()
        for _, row in subset.iterrows():
            year = _year_from_date(row.get("asOfDate"))
            if not year or year in seen:
                continue
            rev = _float(row.get("TotalRevenue"))
            ebitda = _float(row.get("EBITDA"))
            if rev is None and ebitda is None:
                continue
            seen.add(year)
            rows.append({
                "date": str(row.get("asOfDate", ""))[:10],
                "year": year,
                "revenue": rev,
                "ebitda": ebitda,
                "source": "yahoo",
            })
        return sorted(rows, key=lambda x: x["year"])
    except Exception:
        return []


def _fetch_yahoo_prices(ticker: str) -> dict[int, float]:
    try:
        from yahooquery import Ticker

        t = Ticker(ticker.upper())
        hist = t.history(period="6y", interval="1d")
        if hist is None or getattr(hist, "empty", True):
            return {}

        df = hist.reset_index()
        if "date" not in df.columns and "adjclose" in df.columns:
            df = hist.reset_index()
        rows = []
        for _, row in df.iterrows():
            dt = row.get("date")
            price = row.get("adjclose") or row.get("close")
            if dt is not None and price is not None:
                rows.append({"date": str(dt)[:10], "close": float(price)})
        return _year_end_closes(rows, date_key="date", price_key="close")
    except Exception:
        return {}


def _year_end_closes(rows: list[dict], date_key: str, price_key: str) -> dict[int, float]:
    by_year: dict[int, tuple[str, float]] = {}
    for row in rows:
        date_str = str(row.get(date_key, ""))[:10]
        price = _float(row.get(price_key))
        if not date_str or price is None:
            continue
        year = _year_from_date(date_str)
        if not year:
            continue
        if year not in by_year or date_str > by_year[year][0]:
            by_year[year] = (date_str, price)
    return {y: v[1] for y, v in by_year.items()}


def _merge_financial_rows(fmp: list[dict], yahoo: list[dict]) -> list[dict]:
    merged: dict[int, dict] = {}
    for row in yahoo + fmp:  # FMP wins on conflict
        y = row["year"]
        if y not in merged or row.get("source") == "fmp":
            merged[y] = row
    return sorted(merged.values(), key=lambda x: x["year"])


def _build_year_series(financials: list[dict], prices: dict[int, float]) -> list[dict]:
    series = []
    for row in financials:
        year = row["year"]
        series.append({
            "year": year,
            "label": f"FY{year}",
            "revenue": row.get("revenue"),
            "ebitda": row.get("ebitda"),
            "revenue_growth": None,
            "stock_price": prices.get(year),
        })
    return series


def _attach_growth_rates(years: list[dict]) -> None:
    for i in range(1, len(years)):
        prev, curr = years[i - 1], years[i]
        if prev.get("revenue") and curr.get("revenue") and prev["revenue"] > 0:
            curr["revenue_growth"] = round(
                (curr["revenue"] - prev["revenue"]) / prev["revenue"] * 100, 2
            )


def _compute_metrics(years: list[dict]) -> dict:
    revenues = [y["revenue"] for y in years if y.get("revenue")]
    ebitdas = [y["ebitda"] for y in years if y.get("ebitda")]
    growths = [y["revenue_growth"] for y in years if y.get("revenue_growth") is not None]

    return {
        "revenue_cagr": _cagr(revenues),
        "ebitda_cagr": _cagr(ebitdas),
        "growth_consistency_score": _growth_consistency(growths),
        "revenue_volatility": _volatility_pct(growths),
        "ebitda_volatility": _volatility_pct(_yoy_changes(ebitdas)),
    }


def _cagr(values: list[float]) -> Optional[float]:
    clean = [v for v in values if v is not None and v > 0 and math.isfinite(v)]
    if len(clean) < 2:
        return None
    n = len(clean) - 1
    result = ((clean[-1] / clean[0]) ** (1 / n) - 1) * 100
    return round(result, 2) if math.isfinite(result) else None


def _growth_consistency(growth_rates: list[float]) -> float:
    if not growth_rates:
        return 0.0
    positive = sum(1 for g in growth_rates if g > 0)
    positive_ratio = positive / len(growth_rates)
    if len(growth_rates) < 2:
        return round(positive_ratio * 100, 1)
    stdev = statistics.pstdev(growth_rates)
    stability = max(0.0, 1.0 - stdev / 30.0)
    return round(min(100.0, positive_ratio * 60 + stability * 40), 1)


def _volatility_pct(changes: list[float]) -> float:
    if len(changes) < 2:
        return 0.0
    return round(statistics.pstdev(changes), 2)


def _yoy_changes(values: list[float]) -> list[float]:
    changes = []
    for i in range(1, len(values)):
        if values[i - 1] and values[i - 1] > 0:
            changes.append((values[i] - values[i - 1]) / values[i - 1] * 100)
    return changes


def _year_from_date(val: Any) -> Optional[int]:
    if val is None:
        return None
    try:
        s = str(val)[:10]
        return int(s[:4])
    except (TypeError, ValueError):
        return None


def _float(val: Any) -> Optional[float]:
    try:
        if val is None:
            return None
        f = float(val)
        if not math.isfinite(f):
            return None
        return f
    except (TypeError, ValueError):
        return None
