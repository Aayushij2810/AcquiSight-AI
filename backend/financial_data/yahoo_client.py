"""
Yahoo Finance client — global public company search and fundamentals.

Uses Yahoo Search API for name→symbol resolution (any listed equity worldwide)
and yahooquery for fundamentals (more reliable than raw yfinance .info).
"""

from __future__ import annotations

import time
from typing import Any, Optional

import httpx

from financial_data.base import CompanyFinancialSnapshot
from financial_data.industry_map import map_industry
from financial_data.reference_data import display_name_for_ticker

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
_US_EXCHANGES = frozenset({"NYQ", "NMS", "NGM", "NCM", "ASE", "PCX", "BTS", "NAS", "NYS"})
_ADR_EXCHANGES = frozenset({"OID", "PNK", "OTC"})

_cache: dict[str, tuple[float, Any]] = {}
_SNAPSHOT_CACHE_TTL_SEC = 900   # 15 min — balance freshness vs rate limits
_SEARCH_CACHE_TTL_SEC = 300     # 5 min


def _cache_get(key: str, ttl: int = _SNAPSHOT_CACHE_TTL_SEC) -> Any | None:
    entry = _cache.get(key)
    if not entry:
        return None
    ts, value = entry
    if time.time() - ts > ttl:
        del _cache[key]
        return None
    return value


def _cache_set(key: str, value: Any) -> None:
    _cache[key] = (time.time(), value)


def _safe_float(val: Any, default: float = 0.0) -> float:
    try:
        if val is None:
            return default
        return float(val)
    except (TypeError, ValueError):
        return default


def _pick_equity_symbol(quotes: list[dict]) -> str | None:
    equities = [q for q in quotes if q.get("quoteType") == "EQUITY" and q.get("symbol")]
    if not equities:
        return None

    for preferred in (_US_EXCHANGES, _ADR_EXCHANGES):
        for q in equities:
            if q.get("exchange") in preferred:
                return str(q["symbol"])

    return str(equities[0]["symbol"])


def search_ticker(query: str) -> str | None:
    """Resolve a company name or partial ticker to a Yahoo Finance symbol."""
    q = query.strip()
    if not q:
        return None

    cache_key = f"search:{q.lower()}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        with httpx.Client(timeout=10.0, headers={"User-Agent": _USER_AGENT}) as client:
            resp = client.get(
                "https://query2.finance.yahoo.com/v1/finance/search",
                params={"q": q, "quotesCount": 12, "newsCount": 0, "enableFuzzyQuery": True},
            )
            resp.raise_for_status()
            symbol = _pick_equity_symbol(resp.json().get("quotes") or [])
    except Exception:
        symbol = None

    if symbol:
        _cache_set(cache_key, symbol)
    return symbol


def search_company_name(query: str, symbol: str | None = None) -> str | None:
    """Return company name from Yahoo search for a query or symbol."""
    q = (symbol or query).strip()
    if not q:
        return None
    try:
        with httpx.Client(timeout=10.0, headers={"User-Agent": _USER_AGENT}) as client:
            resp = client.get(
                "https://query2.finance.yahoo.com/v1/finance/search",
                params={"q": q, "quotesCount": 8, "newsCount": 0},
            )
            resp.raise_for_status()
            target = symbol.upper() if symbol else None
            for quote in resp.json().get("quotes") or []:
                if quote.get("quoteType") != "EQUITY":
                    continue
                if target and quote.get("symbol") != target:
                    continue
                return quote.get("longname") or quote.get("shortname")
    except Exception:
        pass
    return None


def fetch_company_snapshot(ticker: str, query: str = "") -> CompanyFinancialSnapshot | None:
    """Fetch normalized fundamentals for any public Yahoo Finance symbol."""
    sym = ticker.strip().upper()
    if not sym:
        return None

    cache_key = f"snapshot:{sym}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    for attempt in range(2):
        snapshot = _fetch_snapshot_once(sym, query)
        if snapshot:
            _cache_set(cache_key, snapshot)
            return snapshot
        if attempt == 0:
            time.sleep(0.5)
    return None


def _fetch_snapshot_once(sym: str, query: str) -> CompanyFinancialSnapshot | None:
    try:
        from yahooquery import Ticker

        t = Ticker(sym)
        fd = _module_dict(t.financial_data, sym)
        ap = _module_dict(t.asset_profile, sym)
        ks = _module_dict(t.key_stats, sym)
        sd = _module_dict(t.summary_detail, sym)

        if not fd and not ap and not ks:
            return None

        revenue = _safe_float(fd.get("totalRevenue"))
        ebitda = _safe_float(fd.get("ebitda"))
        if ebitda == 0 and revenue > 0:
            op_margin = _safe_float(fd.get("operatingMargins"))
            ebitda = revenue * op_margin * 1.1 if op_margin else revenue * 0.15

        debt = _safe_float(fd.get("totalDebt"))
        cash = _safe_float(fd.get("totalCash") or fd.get("totalCashFromOperatingActivities"))
        market_cap = ks.get("marketCap") or sd.get("marketCap")
        ev = ks.get("enterpriseValue") or fd.get("enterpriseValue")
        growth = _safe_float(fd.get("revenueGrowth")) * 100 if fd.get("revenueGrowth") else 0.0
        margin = (ebitda / revenue * 100) if revenue > 0 else 0.0

        if revenue == 0 and ebitda == 0 and not market_cap and not ev:
            return None

        historical = _historical_financials(t, sym)
        earnings_dates: list[str] = []
        fiscal_period = historical[0]["period"] if historical else None

        name = (
            ap.get("longName")
            or ap.get("shortName")
            or fd.get("longName")
            or sym
        )
        if name == sym or len(str(name)) <= 5:
            name = (
                search_company_name(query, sym)
                or search_company_name(sym, sym)
                or display_name_for_ticker(sym)
                or name
            )

        snapshot = CompanyFinancialSnapshot(
            company_name=str(name),
            ticker=sym,
            industry=map_industry(ap.get("sector", ""), ap.get("industry", "")),
            sector=ap.get("sector") or "",
            country=ap.get("country") or "United States",
            revenue=revenue,
            ebitda=ebitda,
            net_income=_optional_float(fd.get("netIncomeToCommon") or ks.get("netIncomeToCommon")),
            cash=cash,
            debt=debt,
            market_cap=_optional_float(market_cap),
            enterprise_value=_optional_float(ev),
            revenue_growth=round(growth, 2),
            ebitda_margin=round(margin, 2),
            ev_ebitda_multiple=(float(ev) / ebitda) if ev and ebitda > 0 else None,
            historical_financials=historical,
            earnings_dates=earnings_dates,
            raw_fields={
                "source": "yahooquery",
                "symbol": sym,
                "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "fiscal_period": fiscal_period,
            },
        )
        return snapshot
    except Exception:
        return None


def _module_dict(payload: Any, sym: str) -> dict:
    if not isinstance(payload, dict):
        return {}
    if sym in payload and isinstance(payload[sym], dict):
        return payload[sym]
    if payload and all(isinstance(v, dict) for v in payload.values()):
        return next(iter(payload.values()), {})
    return payload if isinstance(payload, dict) else {}


def _optional_float(val: Any) -> Optional[float]:
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _historical_financials(t: Any, sym: str) -> list[dict]:
    try:
        inc = t.income_statement(frequency="a")
        if inc is None or getattr(inc, "empty", True):
            return []
        subset = inc.loc[sym] if sym in inc.index else inc
        rows: list[dict] = []
        seen: set[str] = set()
        for _, row in subset.iterrows():
            period = str(row.get("asOfDate", ""))[:10]
            if not period or period in seen:
                continue
            rev = row.get("TotalRevenue")
            ebitda = row.get("EBITDA")
            if rev is None and ebitda is None:
                continue
            seen.add(period)
            rows.append({
                "period": period,
                "revenue": _optional_float(rev),
                "ebitda": _optional_float(ebitda),
            })
        return sorted(rows, key=lambda x: x["period"], reverse=True)[:4]
    except Exception:
        return []
