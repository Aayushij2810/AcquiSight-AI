"""
Company Resolution Engine — intelligent ticker and company discovery.

Converts free-form user input into the correct listed symbol before data retrieval.
Resolution order: exact ticker → exact name → partial name → aliases → fuzzy → multi-source search.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

import httpx

from financial_data.company_aliases import COMPANY_DIRECTORY, HISTORICAL_ALIASES, CompanyEntry
from financial_data.reference_data import PRIVATE_COMPANIES

_TICKER_RE = re.compile(r"^[A-Za-z0-9.\-]{1,12}$")
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
_US_EXCHANGES = frozenset({"NYQ", "NMS", "NGM", "NCM", "ASE", "PCX", "BTS", "NAS", "NYS", "NGS"})


@dataclass
class CompanyMatch:
    ticker: str
    company_name: str
    exchange: str = ""
    match_type: str = "search"
    confidence: float = 0.75
    source: str = "combined"


@dataclass
class ResolutionResult:
    query: str
    match: CompanyMatch | None = None
    suggestions: list[CompanyMatch] = field(default_factory=list)
    resolved: bool = False


class CompanyNotFoundError(ValueError):
    def __init__(self, message: str, suggestions: list[CompanyMatch] | None = None):
        super().__init__(message)
        self.suggestions = suggestions or []


def normalize_query(query: str) -> str:
    """Normalize company name — strip legal suffixes only at end of string."""
    key = query.lower().strip().replace(".", "").replace(",", "")
    suffixes = (
        " corporation", " corp.", " corp", " incorporated", " inc.", " inc",
        " platforms", " company", " co.", " ltd.", " ltd", " limited", " plc", " holdings",
    )
    changed = True
    while changed:
        changed = False
        for suffix in suffixes:
            if key.endswith(suffix):
                key = key[: -len(suffix)].strip()
                changed = True
                break
    return key


def _compact(key: str) -> str:
    return key.replace(" ", "").replace("-", "").replace("_", "")


def _fuzzy_score(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _check_private_company(key: str) -> None:
    compact = _compact(key)
    for alias, display_name in PRIVATE_COMPANIES.items():
        alias_compact = _compact(alias)
        if key == alias or compact == alias_compact:
            raise CompanyNotFoundError(
                f"{display_name} is a private company with no public market data. "
                "Enter a listed ticker or public company name."
            )
        if len(key) >= 4 and len(alias) >= 4 and (alias in key or key in alias):
            raise CompanyNotFoundError(
                f"{display_name} is a private company with no public market data. "
                "Enter a listed ticker or public company name."
            )


def _entry_to_match(entry: CompanyEntry, match_type: str, confidence: float, source: str) -> CompanyMatch:
    return CompanyMatch(
        ticker=entry.ticker,
        company_name=entry.company_name,
        match_type=match_type,
        confidence=confidence,
        source=source,
    )


def _search_local(query: str, limit: int = 10) -> list[CompanyMatch]:
    key = normalize_query(query)
    compact = _compact(key)
    scored: list[tuple[float, CompanyMatch]] = []

    for entry in COMPANY_DIRECTORY:
        candidates = (entry.company_name.lower(), *entry.aliases, entry.ticker.lower())
        best = 0.0
        match_type = "partial_name"

        if key == entry.ticker.lower() or compact == _compact(entry.ticker):
            best = 1.0
            match_type = "exact_ticker"
        elif key == entry.company_name.lower() or compact == _compact(entry.company_name):
            best = 0.98
            match_type = "exact_name"
        elif key in HISTORICAL_ALIASES and HISTORICAL_ALIASES[key] == entry.ticker:
            best = 0.96
            match_type = "alias"
        else:
            for cand in candidates:
                if key == cand or compact == _compact(cand):
                    best = max(best, 0.95)
                    match_type = "alias" if cand in entry.aliases else "exact_name"
                elif len(key) >= 4 and len(cand) >= 4 and (key in cand or cand in key):
                    best = max(best, 0.88)
                    match_type = "partial_name"
                else:
                    ratio = _fuzzy_score(key, cand)
                    if ratio >= 0.72:
                        best = max(best, ratio * 0.92)
                        match_type = "fuzzy"

        if best >= 0.72:
            scored.append((best, _entry_to_match(entry, match_type, best, "local_cache")))

    scored.sort(key=lambda x: x[0], reverse=True)
    seen: set[str] = set()
    results: list[CompanyMatch] = []
    for _, match in scored:
        if match.ticker in seen:
            continue
        seen.add(match.ticker)
        results.append(match)
        if len(results) >= limit:
            break
    return results


def _search_yahoo(query: str, limit: int = 10) -> list[CompanyMatch]:
    try:
        with httpx.Client(timeout=10.0, headers={"User-Agent": _USER_AGENT}) as client:
            resp = client.get(
                "https://query2.finance.yahoo.com/v1/finance/search",
                params={"q": query, "quotesCount": limit, "newsCount": 0, "enableFuzzyQuery": True},
            )
            if resp.status_code != 200:
                return []
            quotes = resp.json().get("quotes") or []
    except Exception:
        return []

    results: list[CompanyMatch] = []
    for i, q in enumerate(quotes):
        if q.get("quoteType") != "EQUITY" or not q.get("symbol"):
            continue
        score = float(q.get("score") or 0)
        confidence = min(0.99, 0.7 + (score / max(score, 1)) * 0.01 + (0.05 if i == 0 else 0))
        if q.get("exchange") in _US_EXCHANGES:
            confidence += 0.03
        results.append(CompanyMatch(
            ticker=str(q["symbol"]),
            company_name=str(q.get("longname") or q.get("shortname") or q["symbol"]),
            exchange=str(q.get("exchange") or ""),
            match_type="yahoo_search",
            confidence=min(confidence, 0.99),
            source="yahoo_finance",
        ))
    return results


def _search_nasdaq(query: str, limit: int = 10) -> list[CompanyMatch]:
    try:
        with httpx.Client(timeout=10.0, headers={"User-Agent": _USER_AGENT, "Accept": "application/json"}) as client:
            resp = client.get(
                f"https://api.nasdaq.com/api/autocomplete/slookup/10",
                params={"search": query},
            )
            if resp.status_code != 200:
                return []
            rows = resp.json().get("data") or []
    except Exception:
        return []

    results: list[CompanyMatch] = []
    for i, row in enumerate(rows[:limit]):
        symbol = row.get("symbol")
        if not symbol:
            continue
        results.append(CompanyMatch(
            ticker=str(symbol),
            company_name=str(row.get("name") or symbol).replace(" Common Stock", ""),
            exchange=str(row.get("exchange") or "NASDAQ"),
            match_type="nasdaq_directory",
            confidence=0.85 - i * 0.03,
            source="nasdaq",
        ))
    return results


def _search_fmp(query: str, limit: int = 8) -> list[CompanyMatch]:
    import os
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        return []
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                "https://financialmodelingprep.com/api/v3/search",
                params={"query": query, "limit": limit, "apikey": api_key},
            )
            if resp.status_code != 200:
                return []
            rows = resp.json() or []
    except Exception:
        return []

    results: list[CompanyMatch] = []
    for i, row in enumerate(rows):
        symbol = row.get("symbol")
        if not symbol:
            continue
        results.append(CompanyMatch(
            ticker=str(symbol),
            company_name=str(row.get("name") or symbol),
            exchange=str(row.get("exchangeShortName") or row.get("stockExchange") or ""),
            match_type="fmp_search",
            confidence=0.82 - i * 0.02,
            source="financial_modeling_prep",
        ))
    return results


def _merge_matches(*sources: list[CompanyMatch]) -> list[CompanyMatch]:
    merged: dict[str, CompanyMatch] = {}
    for source_list in sources:
        for m in source_list:
            existing = merged.get(m.ticker)
            if existing is None or m.confidence > existing.confidence:
                merged[m.ticker] = m
            else:
                existing.confidence = min(0.99, existing.confidence + 0.02)
    return sorted(merged.values(), key=lambda x: x.confidence, reverse=True)


def search_companies(query: str, limit: int = 10) -> list[CompanyMatch]:
    """Multi-source autocomplete / discovery search."""
    q = query.strip()
    if not q or len(q) < 1:
        return []
    return _merge_matches(
        _search_local(q, limit),
        _search_yahoo(q, limit),
        _search_nasdaq(q, limit),
        _search_fmp(q, limit),
    )[:limit]


def _looks_like_ticker(q: str) -> bool:
    if not _TICKER_RE.fullmatch(q):
        return False
    if "." in q or any(c.isdigit() for c in q):
        return True
    return q.isalpha() and len(q) <= 5 and q.isupper()


def resolve_company(query: str) -> ResolutionResult:
    """
    Resolve user input to the best ticker match.

    Steps 1–5: exact ticker → exact name → partial → aliases → fuzzy + multi-source.
    """
    q = query.strip()
    if not q:
        raise CompanyNotFoundError("Query cannot be empty.")

    key = normalize_query(q)
    _check_private_company(key)

    suggestions = search_companies(q, limit=12)

    # Step 1: Exact ticker — only if it appears in validated search results.
    upper = q.upper()
    if _looks_like_ticker(q):
        for s in suggestions:
            if s.ticker.upper() == upper:
                s.match_type = "exact_ticker"
                s.confidence = max(s.confidence, 0.99)
                return ResolutionResult(query=q, match=s, suggestions=[x for x in suggestions if x.ticker != s.ticker], resolved=True)

    # Step 4: Historical aliases (Google → GOOGL, Facebook → META, Adobe typo ADOBE → ADBE).
    if key in HISTORICAL_ALIASES:
        ticker = HISTORICAL_ALIASES[key]
        match = _match_for_ticker(ticker, suggestions) or CompanyMatch(
            ticker=ticker,
            company_name=_name_for_ticker(ticker),
            match_type="alias",
            confidence=0.96,
            source="historical_alias",
        )
        return ResolutionResult(
            query=q,
            match=match,
            suggestions=[x for x in suggestions if x.ticker != match.ticker],
            resolved=True,
        )

    # Steps 2–3 & 5: Local exact / partial / fuzzy (high-confidence local hits).
    local = _search_local(q, limit=5)
    if local and local[0].confidence >= 0.88:
        best = local[0]
        if best.match_type in ("exact_ticker", "exact_name", "alias", "partial_name"):
            return ResolutionResult(
                query=q,
                match=best,
                suggestions=_merge_matches(local[1:], suggestions)[:8],
                resolved=True,
            )

    # Multi-source: best overall suggestion (handles ADOBE → ADBE, Meta, Nvidia, etc.).
    if suggestions:
        best = suggestions[0]
        # Boost if normalized query matches company name closely.
        name_ratio = _fuzzy_score(key, normalize_query(best.company_name))
        if name_ratio >= 0.75:
            best.confidence = max(best.confidence, 0.9)
            best.match_type = "fuzzy" if name_ratio < 0.95 else "partial_name"
        return ResolutionResult(
            query=q,
            match=best,
            suggestions=suggestions[1:9],
            resolved=True,
        )

    raise CompanyNotFoundError(
        f"Unable to find company '{query}'. Try a ticker (MSFT, ADBE) or company name (Microsoft, Adobe).",
        suggestions=local[:5],
    )


def resolve_ticker(query: str) -> str:
    """Backward-compatible ticker resolution."""
    result = resolve_company(query)
    if result.match:
        return result.match.ticker
    raise CompanyNotFoundError(f"Could not resolve '{query}' to a listed ticker.")


def _match_for_ticker(ticker: str, suggestions: list[CompanyMatch]) -> CompanyMatch | None:
    for s in suggestions:
        if s.ticker.upper() == ticker.upper():
            return s
    return None


def _name_for_ticker(ticker: str) -> str:
    for entry in COMPANY_DIRECTORY:
        if entry.ticker.upper() == ticker.upper():
            return entry.company_name
    return ticker
