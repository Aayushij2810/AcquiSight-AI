"""
AcquiSight Copilot — grounded investment Q&A over platform data.

Answers are generated exclusively from:
  • Portfolio pipeline
  • Investment / risk scores
  • Valuation & comps
  • Historical trends
  • Timing scores
"""

from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Optional

from models import DealScreenRequest, DealScreenResponse, Industry
from portfolio import build_analytics, compute_priority_score
from scoring import compute_scores
from valuation import compute_enterprise_value
from risk import compute_risk_assessment
from comps import get_comps
from recommendation import get_recommendation
from timing_engine import compute_timing_analysis

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from financial_data_gateway import fetch_company_intelligence
    from financial_data.company_resolver import search_companies, CompanyNotFoundError
    INTEL_AVAILABLE = True
except Exception:
    INTEL_AVAILABLE = False

try:
    from historical_trends import fetch_historical_trends
    HISTORICAL_AVAILABLE = True
except Exception:
    HISTORICAL_AVAILABLE = False


# ---------------------------------------------------------------------------
# Industry mapping (gateway strings → screening enum)
# ---------------------------------------------------------------------------

_INDUSTRY_KEYWORDS: list[tuple[str, Industry]] = [
    ("saas", Industry.SAAS),
    ("software", Industry.SAAS),
    ("fintech", Industry.FINTECH),
    ("financial", Industry.FINTECH),
    ("health", Industry.HEALTHCARE),
    ("pharma", Industry.PHARMA_BIOTECH),
    ("biotech", Industry.PHARMA_BIOTECH),
    ("manufactur", Industry.MANUFACTURING),
    ("consumer", Industry.CONSUMER),
    ("energy", Industry.ENERGY),
    ("real estate", Industry.REAL_ESTATE),
    ("retail", Industry.RETAIL),
    ("telecom", Industry.TELECOMMUNICATIONS),
    ("media", Industry.MEDIA_ENTERTAINMENT),
    ("entertainment", Industry.MEDIA_ENTERTAINMENT),
    ("logistics", Industry.LOGISTICS_TRANSPORTATION),
    ("transport", Industry.LOGISTICS_TRANSPORTATION),
    ("insurance", Industry.INSURANCE),
    ("automotive", Industry.AUTOMOTIVE),
    ("auto", Industry.AUTOMOTIVE),
    ("aerospace", Industry.AEROSPACE_DEFENSE),
    ("defense", Industry.AEROSPACE_DEFENSE),
    ("education", Industry.EDUCATION),
    ("hospitality", Industry.HOSPITALITY_LEISURE),
    ("cyber", Industry.CYBERSECURITY),
    ("e-commerce", Industry.ECOMMERCE),
    ("ecommerce", Industry.ECOMMERCE),
    ("industrial", Industry.INDUSTRIAL_SERVICES),
    ("technology", Industry.TECHNOLOGY),
    ("tech", Industry.TECHNOLOGY),
    ("semiconductor", Industry.TECHNOLOGY),
]


def _map_industry(raw: str | None) -> Industry:
    if not raw:
        return Industry.TECHNOLOGY
    lower = raw.lower()
    for keyword, industry in _INDUSTRY_KEYWORDS:
        if keyword in lower:
            return industry
    return Industry.OTHER


# ---------------------------------------------------------------------------
# Query parsing
# ---------------------------------------------------------------------------

_STOPWORDS = re.compile(
    r"\b(?:why|does|do|what|are|the|biggest|risks|for|how|which|company|companies|"
    r"in|my|portfolio|has|have|highest|lowest|best|worst|top|risk|adjusted|return|"
    r"score|scores|scored|higher|lower|better|worse|than|compare|comparison|between|"
    r"vs|versus|and|or|a|an|is|was|tell|me|about|show|explain|give|their|its|"
    r"with|from|using|please|can|you|would|should|could|big|main|key|major)\b",
    re.I,
)


def _extract_companies(query: str, portfolio_names: list[str]) -> list[str]:
    found: list[str] = []
    ql = query.lower()

    for name in sorted(portfolio_names, key=len, reverse=True):
        if name.lower() in ql and name not in found:
            found.append(name)

    segments = re.split(
        r"\b(?:vs\.?|versus|compared\s+to|compare|than|between|and)\b",
        query,
        flags=re.I,
    )
    if len(segments) <= 1:
        segments = [query]

    if INTEL_AVAILABLE:
        for seg in segments:
            cleaned = _STOPWORDS.sub(" ", seg).strip()
            cleaned = re.sub(r"\s+", " ", cleaned)
            if len(cleaned) < 2:
                continue
            try:
                matches = search_companies(cleaned, limit=1)
                if matches and matches[0].confidence >= 0.45:
                    name = matches[0].company_name
                    if name not in found:
                        found.append(name)
            except Exception:
                pass

        # Whole-query fallback when split parsing misses names (e.g. "Tesla risks")
        if not found:
            try:
                matches = search_companies(query, limit=3)
                for m in matches:
                    if m.confidence >= 0.55 and m.company_name not in found:
                        found.append(m.company_name)
            except Exception:
                pass

    return found[:4]


def _classify_intent(query: str, companies: list[str]) -> str:
    ql = query.lower()
    portfolio_q = any(k in ql for k in ("portfolio", "pipeline", "my deals", "my holdings"))

    if portfolio_q and any(
        k in ql for k in ("risk-adjusted", "risk adjusted", "priority", "best return", "highest return", "top")
    ):
        return "portfolio_ranking"
    if portfolio_q:
        return "portfolio_overview"
    if any(k in ql for k in ("risk", "risks", "concern", "downside", "threat")) and companies:
        return "risk_analysis"
    if any(k in ql for k in ("why", "higher", "lower", "better score", "scores higher", "score higher")) and len(companies) >= 2:
        return "score_comparison"
    if any(k in ql for k in ("compare", "vs", "versus", "difference", "between")) and len(companies) >= 2:
        return "company_comparison"
    if len(companies) >= 2:
        return "company_comparison"
    if len(companies) == 1:
        if any(k in ql for k in ("risk", "risks")):
            return "risk_analysis"
        return "company_summary"
    return "general"


# ---------------------------------------------------------------------------
# Screening pipeline (no DB persistence)
# ---------------------------------------------------------------------------


def _run_screen(payload: DealScreenRequest) -> DealScreenResponse:
    ebitda_margin = (payload.ebitda / payload.revenue) * 100 if payload.revenue else 0.0
    net_debt = payload.debt - payload.cash
    debt_to_ebitda = (payload.debt / payload.ebitda) if payload.ebitda > 0 else None
    dte = debt_to_ebitda if debt_to_ebitda is not None else 99.0

    comps_result = get_comps(industry=payload.industry.value, ebitda=payload.ebitda)
    valuation = compute_enterprise_value(
        ebitda=payload.ebitda,
        debt=payload.debt,
        cash=payload.cash,
        industry=payload.industry.value,
        market_cap=payload.market_cap,
        base_multiple=comps_result.base_multiple,
    )
    scores, investment_score, score_breakdown = compute_scores(
        ebitda_margin=ebitda_margin,
        growth_rate=payload.growth_rate,
        debt_to_ebitda=dte,
        revenue=payload.revenue,
        cash=payload.cash,
        debt=payload.debt,
        industry=payload.industry.value,
    )
    risk_score, risk_label, risk_breakdown, risk_factors = compute_risk_assessment(
        debt_to_ebitda=dte,
        ebitda_margin=ebitda_margin,
        growth_rate=payload.growth_rate,
        revenue=payload.revenue,
        industry=payload.industry.value,
        country=payload.country,
    )
    rec, rec_color = get_recommendation(
        revenue=payload.revenue,
        investment_score=investment_score,
        risk_score=risk_score,
    )
    timing = compute_timing_analysis(
        company_name=payload.company_name,
        industry=payload.industry.value,
        revenue=payload.revenue,
        ebitda=payload.ebitda,
        growth_rate=payload.growth_rate,
        ebitda_margin=ebitda_margin,
        debt_to_ebitda=debt_to_ebitda,
        enterprise_value=valuation.enterprise_value,
        investment_score=investment_score,
        risk_score=risk_score,
        scores=scores,
        comps=comps_result,
        market_cap=payload.market_cap,
    )
    return DealScreenResponse(
        company_name=payload.company_name,
        industry=payload.industry.value,
        ebitda_margin=round(ebitda_margin, 2),
        net_debt=net_debt,
        debt_to_ebitda=round(debt_to_ebitda, 2) if debt_to_ebitda is not None else None,
        enterprise_value=valuation.enterprise_value,
        investment_score=investment_score,
        risk_score=risk_score,
        risk_label=risk_label,
        scores=scores,
        score_breakdown=score_breakdown,
        recommendation=rec,
        recommendation_color=rec_color,
        valuation=valuation,
        risk_factors=risk_factors,
        risk_breakdown=risk_breakdown,
        comps=comps_result,
        timing=timing,
    )


def _screen_from_intel(intel: dict) -> DealScreenResponse:
    revenue = float(intel.get("revenue") or 0)
    if revenue <= 0:
        raise ValueError(f"Insufficient revenue data for {intel.get('company_name', 'company')}.")
    return _run_screen(DealScreenRequest(
        company_name=intel["company_name"],
        industry=_map_industry(intel.get("industry") or intel.get("sector")),
        revenue=revenue,
        ebitda=float(intel.get("ebitda") or 0),
        growth_rate=float(intel.get("revenue_growth") or 0),
        debt=float(intel.get("debt") or 0),
        cash=float(intel.get("cash") or 0),
        country=intel.get("country") or "United States",
        market_cap=intel.get("market_cap"),
    ))


# ---------------------------------------------------------------------------
# Company context
# ---------------------------------------------------------------------------


@dataclass
class CompanyContext:
    company_name: str
    ticker: Optional[str] = None
    screen: Optional[DealScreenResponse] = None
    historical: Optional[dict] = None
    priority_score: Optional[float] = None
    from_portfolio: bool = False
    data_layers: list[str] = field(default_factory=list)
    error: Optional[str] = None


def _find_portfolio_opp(name: str, opportunities: list[Any]) -> Any | None:
    nl = name.lower()
    for opp in opportunities:
        if opp.company_name.lower() == nl or nl in opp.company_name.lower():
            return opp
    return None


def _wants_historical(message: str) -> bool:
    ql = message.lower()
    return any(k in ql for k in (
        "historical", "trend", "trends", "cagr", "volatility",
        "5-year", "5 year", "five year", "revenue growth over",
    ))


def _load_company_context(name: str, opportunities: list[Any], include_historical: bool = False) -> CompanyContext:
    ctx = CompanyContext(company_name=name, data_layers=[])

    opp = _find_portfolio_opp(name, opportunities)
    if opp:
        ctx.from_portfolio = True
        ctx.priority_score = opp.priority_score
        ctx.data_layers.append("Portfolio Data")
        if opp.screen_result_json:
            try:
                ctx.screen = DealScreenResponse(**opp.screen_result_json)
                ctx.ticker = (opp.screen_result_json.get("company_name") or name)[:12]
            except Exception:
                pass

    if not ctx.screen and INTEL_AVAILABLE:
        try:
            intel = fetch_company_intelligence(name)
            ctx.ticker = intel.get("ticker")
            ctx.screen = _screen_from_intel(intel)
            ctx.data_layers.extend(["Company Intelligence", "Investment Scores", "Risk Scores", "Valuation Metrics", "Timing Scores"])
        except (CompanyNotFoundError, ValueError) as exc:
            ctx.error = str(exc)
            return ctx
        except Exception as exc:
            ctx.error = f"Unable to load data for {name}: {exc}"
            return ctx
    elif ctx.screen:
        ctx.data_layers.extend(["Investment Scores", "Risk Scores", "Valuation Metrics", "Timing Scores"])

    if include_historical and HISTORICAL_AVAILABLE:
        try:
            hist = fetch_historical_trends(name)
            ctx.historical = hist
            if "Historical Trends" not in ctx.data_layers:
                ctx.data_layers.append("Historical Trends")
        except Exception:
            pass

    return ctx


def _screen_to_dict(screen: DealScreenResponse) -> dict:
    return screen.model_dump()


# ---------------------------------------------------------------------------
# Source metrics
# ---------------------------------------------------------------------------


def _fmt_money(v: float | None) -> str:
    if v is None:
        return "—"
    if abs(v) >= 1e12:
        return f"${v / 1e12:.2f}T"
    if abs(v) >= 1e9:
        return f"${v / 1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"${v / 1e6:.1f}M"
    return f"${v:,.0f}"


def _collect_company_sources(ctx: CompanyContext) -> list[dict]:
    if not ctx.screen:
        return []
    s = ctx.screen
    company = ctx.company_name
    sources = [
        {"label": "Investment Score", "value": f"{s.investment_score}/100", "company": company, "category": "Investment Scores"},
        {"label": "Risk Score", "value": f"{s.risk_score}/100 ({s.risk_label})", "company": company, "category": "Risk Scores"},
        {"label": "Recommendation", "value": s.recommendation, "company": company, "category": "Investment Scores"},
        {"label": "Enterprise Value", "value": _fmt_money(s.enterprise_value), "company": company, "category": "Valuation Metrics"},
        {"label": "EV/EBITDA Multiple", "value": f"{s.comps.base_multiple:.1f}x (base comp)", "company": company, "category": "Valuation Metrics"},
        {"label": "Timing Score", "value": f"{s.timing.timing_score}/100 — {s.timing.status}", "company": company, "category": "Timing Scores"},
        {"label": "Growth Score", "value": f"{s.scores.growth}/100", "company": company, "category": "Investment Scores"},
        {"label": "Profitability Score", "value": f"{s.scores.profitability}/100", "company": company, "category": "Investment Scores"},
        {"label": "Leverage Score", "value": f"{s.scores.leverage}/100", "company": company, "category": "Investment Scores"},
    ]
    if ctx.priority_score is not None and ctx.from_portfolio:
        sources.append({
            "label": "Priority Score (risk-adjusted)",
            "value": f"{ctx.priority_score:.1f}",
            "company": company,
            "category": "Portfolio Data",
        })
    if ctx.historical:
        m = ctx.historical.get("metrics", {})
        if m.get("revenue_cagr") is not None:
            sources.append({
                "label": "Revenue CAGR (5Y)",
                "value": f"{m['revenue_cagr']:+.1f}%",
                "company": company,
                "category": "Historical Trends",
            })
        if m.get("growth_consistency_score") is not None:
            sources.append({
                "label": "Growth Consistency",
                "value": f"{m['growth_consistency_score']}/100",
                "company": company,
                "category": "Historical Trends",
            })
    return sources


def _collect_risk_sources(ctx: CompanyContext) -> list[dict]:
    if not ctx.screen:
        return []
    sources = []
    severity_rank = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    factors = sorted(ctx.screen.risk_factors, key=lambda f: severity_rank.get(f.severity, 9))
    for rf in factors[:5]:
        sources.append({
            "label": rf.name,
            "value": f"{rf.severity} — {rf.description[:120]}",
            "company": ctx.company_name,
            "category": "Risk Scores",
        })
    return sources


# ---------------------------------------------------------------------------
# Template responses (no OpenAI)
# ---------------------------------------------------------------------------


def _template_score_comparison(a: CompanyContext, b: CompanyContext) -> str:
    if not a.screen or not b.screen:
        return "I couldn't load screening data for one or both companies. Try screening them first or check the company name."
    sa, sb = a.screen, b.screen
    higher = a.company_name if sa.investment_score >= sb.investment_score else b.company_name
    lower = b.company_name if higher == a.company_name else a.company_name
    hs = sa if sa.investment_score >= sb.investment_score else sb
    ls = sb if hs is sa else sa
    diff = hs.investment_score - ls.investment_score

    lines = [
        f"**{higher}** scores **{hs.investment_score}/100** vs **{lower}** at **{ls.investment_score}/100** "
        f"(+{diff} point difference), based on AcquiSight's investment scoring model.",
        "",
        "**Key dimension gaps:**",
    ]
    dims = [
        ("Growth", hs.scores.growth, ls.scores.growth),
        ("Profitability", hs.scores.profitability, ls.scores.profitability),
        ("Leverage", hs.scores.leverage, ls.scores.leverage),
        ("Revenue Quality", hs.scores.revenue_quality, ls.scores.revenue_quality),
        ("Financial Health", hs.scores.financial_health, ls.scores.financial_health),
    ]
    for label, hv, lv in dims:
        gap = hv - lv
        if abs(gap) >= 3:
            direction = higher if gap > 0 else lower
            lines.append(f"- **{label}:** {direction} leads by {abs(gap)} pts ({hv} vs {lv})")

    lines.extend([
        "",
        f"**Risk context:** {higher} risk {hs.risk_score}/100 ({hs.risk_label}) vs {lower} {ls.risk_score}/100 ({ls.risk_label}).",
        f"**Timing:** {higher} {hs.timing.timing_score}/100 ({hs.timing.status}) vs {lower} {ls.timing.timing_score}/100 ({ls.timing.status}).",
        "",
        "**Score breakdown (weighted contributions):**",
    ])
    for item in hs.score_breakdown:
        other = next((x for x in ls.score_breakdown if x.dimension == item.dimension), None)
        other_pts = other.raw_score if other else 0
        if abs(item.raw_score - other_pts) >= 3:
            lines.append(f"- {item.dimension}: {higher} {item.raw_score} vs {lower} {other_pts} (weight {item.weight_pct:.0f}%)")

    return "\n".join(lines)


def _template_company_comparison(contexts: list[CompanyContext]) -> str:
    valid = [c for c in contexts if c.screen]
    if len(valid) < 2:
        return "I need at least two companies with screening data to compare. Check the names and try again."

    lines = ["**Side-by-side comparison** (AcquiSight data only):", ""]
    headers = [c.company_name for c in valid]
    lines.append("| Metric | " + " | ".join(headers) + " |")
    lines.append("| --- | " + " | ".join(["---"] * len(valid)) + " |")

    rows = [
        ("Investment Score", lambda c: f"{c.screen.investment_score}/100"),
        ("Risk Score", lambda c: f"{c.screen.risk_score}/100"),
        ("Timing Score", lambda c: f"{c.screen.timing.timing_score}/100"),
        ("Enterprise Value", lambda c: _fmt_money(c.screen.enterprise_value)),
        ("EV/EBITDA", lambda c: f"{c.screen.comps.base_multiple:.1f}x"),
        ("EBITDA Margin", lambda c: f"{c.screen.ebitda_margin:.1f}%"),
        ("Recommendation", lambda c: c.screen.recommendation),
    ]
    for label, fn in rows:
        lines.append("| " + label + " | " + " | ".join(fn(c) for c in valid) + " |")

    lines.append("")
    best = max(valid, key=lambda c: c.screen.investment_score)
    safest = min(valid, key=lambda c: c.screen.risk_score)
    lines.append(
        f"**Highest investment score:** {best.company_name} ({best.screen.investment_score}/100). "
        f"**Lowest risk:** {safest.company_name} ({safest.screen.risk_score}/100)."
    )
    return "\n".join(lines)


def _template_risk_analysis(ctx: CompanyContext) -> str:
    if not ctx.screen:
        return ctx.error or f"No risk data available for {ctx.company_name}."
    s = ctx.screen
    severity_rank = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    factors = sorted(s.risk_factors, key=lambda f: severity_rank.get(f.severity, 9))

    lines = [
        f"**{ctx.company_name}** — Risk Score **{s.risk_score}/100** ({s.risk_label})",
        "",
        "**Top risk factors** (from AcquiSight risk engine):",
    ]
    for i, rf in enumerate(factors[:5], 1):
        lines.append(f"{i}. **{rf.name}** [{rf.severity}] — {rf.description}")
        lines.append(f"   *Mitigation:* {rf.mitigation}")

    lines.extend([
        "",
        f"**Timing risk catalysts:** {len(s.timing.risk_catalysts)} identified. "
        f"Entry window: {s.timing.entry_window_assessment}.",
    ])
    return "\n".join(lines)


def _template_portfolio_ranking(opportunities: list[Any]) -> str:
    if not opportunities:
        return "Your portfolio is empty. Screen companies and add them to the pipeline to run portfolio analysis."

    ranked = sorted(
        opportunities,
        key=lambda o: compute_priority_score(o.investment_score, o.risk_score),
        reverse=True,
    )
    top = ranked[0]
    ps = compute_priority_score(top.investment_score, top.risk_score)

    lines = [
        f"**{top.company_name}** has the highest risk-adjusted priority score in your portfolio: **{ps:.1f}**.",
        "",
        "Priority Score = (Investment Score × 60%) + (100 − Risk Score) × 40%",
        "",
        f"- Investment Score: **{top.investment_score}/100**",
        f"- Risk Score: **{top.risk_score}/100**",
        f"- Recommendation: **{top.recommendation}**",
    ]
    if top.timing_score:
        lines.append(f"- Timing Score: **{top.timing_score}/100**")
    if len(ranked) > 1:
        lines.append("")
        lines.append("**Full ranking:**")
        for i, o in enumerate(ranked[:5], 1):
            p = compute_priority_score(o.investment_score, o.risk_score)
            lines.append(f"{i}. {o.company_name} — Priority {p:.1f} (Inv {o.investment_score}, Risk {o.risk_score})")
    return "\n".join(lines)


def _template_portfolio_overview(opportunities: list[Any]) -> str:
    analytics = build_analytics(opportunities)
    if analytics["total_opportunities"] == 0:
        return "Your portfolio is empty. Add screened companies from Portfolio Mode."
    h = analytics["highlights"]
    return (
        f"Your pipeline has **{analytics['total_opportunities']}** opportunities. "
        f"Avg investment score **{analytics['avg_investment_score']:.0f}/100**, "
        f"avg risk **{analytics['avg_risk_score']:.0f}/100**. "
        f"Best priority: **{h['best_opportunity']['company_name'] if h['best_opportunity'] else 'N/A'}**. "
        f"Safest: **{h['safest_investment']['company_name'] if h['safest_investment'] else 'N/A'}**."
    )


def _template_response(intent: str, contexts: list[CompanyContext], opportunities: list[Any]) -> str:
    errors = [f"**{c.company_name}:** {c.error}" for c in contexts if c.error]
    error_block = ("\n\n".join(errors) + "\n\n") if errors else ""

    if intent == "score_comparison" and len(contexts) >= 2:
        if not contexts[0].screen or not contexts[1].screen:
            return error_block + "I couldn't load screening data for one or both companies. Check the names and try again."
        return error_block + _template_score_comparison(contexts[0], contexts[1])
    if intent == "company_comparison":
        valid = [c for c in contexts if c.screen]
        if len(valid) < 2:
            return error_block + "I need at least two companies with screening data to compare. Check the names and try again."
        return error_block + _template_company_comparison(contexts)
    if intent == "risk_analysis" and contexts:
        if not contexts[0].screen:
            return error_block + (contexts[0].error or f"No risk data available for {contexts[0].company_name}.")
        return error_block + _template_risk_analysis(contexts[0])
    if intent == "portfolio_ranking":
        return _template_portfolio_ranking(opportunities)
    if intent == "portfolio_overview":
        return _template_portfolio_overview(opportunities)
    if contexts and contexts[0].screen:
        c = contexts[0]
        s = c.screen
        body = (
            f"**{c.company_name}** — Investment Score **{s.investment_score}/100**, "
            f"Risk **{s.risk_score}/100** ({s.risk_label}), Timing **{s.timing.timing_score}/100** ({s.timing.status}).\n\n"
            f"- Recommendation: {s.recommendation}\n"
            f"- Enterprise Value: {_fmt_money(s.enterprise_value)} at {s.comps.base_multiple:.1f}x EV/EBITDA\n"
            f"- EBITDA Margin: {s.ebitda_margin:.1f}%\n"
            f"- Growth Score: {s.scores.growth}/100 · Profitability: {s.scores.profitability}/100"
        )
        return error_block + body
    if errors:
        return error_block + "Unable to load company data. Try the full company name or ticker."
    return (
        "I can answer questions about investment scores, risk, valuations, timing, historical trends, "
        "and your portfolio. Try:\n"
        "- *Why does NVIDIA score higher than Microsoft?*\n"
        "- *Compare Meta vs Alphabet*\n"
        "- *What are the biggest risks for Tesla?*\n"
        "- *Which company in my portfolio has the highest risk-adjusted return?*"
    )


def _should_use_template(intent: str, contexts: list[CompanyContext], opportunities: list[Any]) -> bool:
    """Structured intents use deterministic templates — avoids AI inventing scores."""
    if intent in ("portfolio_ranking", "portfolio_overview"):
        return True
    if intent == "score_comparison" and len(contexts) >= 2:
        return bool(contexts[0].screen and contexts[1].screen)
    if intent == "company_comparison":
        return sum(1 for c in contexts if c.screen) >= 2
    if intent == "risk_analysis" and contexts:
        return bool(contexts[0].screen)
    if intent == "company_summary" and contexts:
        return bool(contexts[0].screen)
    return False


def _load_contexts_parallel(
    names: list[str],
    opportunities: list[Any],
    include_historical: bool,
) -> list[CompanyContext]:
    if not names:
        return []
    if len(names) == 1:
        return [_load_company_context(names[0], opportunities, include_historical)]

    results: dict[str, CompanyContext] = {}
    with ThreadPoolExecutor(max_workers=min(len(names), 3)) as pool:
        futures = {
            pool.submit(_load_company_context, name, opportunities, include_historical): name
            for name in names
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as exc:
                results[name] = CompanyContext(company_name=name, error=str(exc))

    return [results[n] for n in names if n in results]


# ---------------------------------------------------------------------------
# OpenAI response
# ---------------------------------------------------------------------------


def _is_valid_api_key(api_key: str | None) -> bool:
    if not api_key:
        return False
    normalized = api_key.strip()
    if normalized in {"", "sk-your-key-here"}:
        return False
    return normalized.startswith("sk-") and len(normalized) > 20


def _build_context_payload(
    intent: str,
    contexts: list[CompanyContext],
    opportunities: list[Any],
) -> dict:
    payload: dict[str, Any] = {"intent": intent}
    if intent in ("portfolio_ranking", "portfolio_overview"):
        analytics = build_analytics(opportunities)
        payload["portfolio"] = {
            "analytics": analytics,
            "companies": [
                {
                    "company_name": o.company_name,
                    "investment_score": o.investment_score,
                    "risk_score": o.risk_score,
                    "priority_score": o.priority_score,
                    "timing_score": o.timing_score,
                    "recommendation": o.recommendation,
                    "enterprise_value": o.enterprise_value,
                    "growth_rate": o.growth_rate,
                }
                for o in opportunities
            ],
        }
    payload["companies"] = []
    for ctx in contexts:
        entry: dict[str, Any] = {
            "company_name": ctx.company_name,
            "ticker": ctx.ticker,
            "from_portfolio": ctx.from_portfolio,
            "priority_score": ctx.priority_score,
            "error": ctx.error,
        }
        if ctx.screen:
            entry["screen"] = _screen_to_dict(ctx.screen)
        if ctx.historical:
            entry["historical_trends"] = ctx.historical
        payload["companies"].append(entry)
    return payload


async def _generate_ai_answer(message: str, context: dict) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not _is_valid_api_key(api_key) or not OPENAI_AVAILABLE:
        return None

    client = AsyncOpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    system = (
        "You are AcquiSight Copilot, an institutional investment research assistant. "
        "Answer ONLY using the JSON context provided — never use outside knowledge or invent numbers. "
        "If data is missing, say so clearly. "
        "Write in clear, professional prose (markdown allowed). "
        "Reference specific scores, metrics, and company names from the context. "
        "Do not provide buy/sell advice; frame as analytical research."
    )
    user = f"Context:\n```json\n{json.dumps(context, default=str)[:12000]}\n```\n\nQuestion: {message}"

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.25,
            max_tokens=900,
        )
        return (response.choices[0].message.content or "").strip() or None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def run_copilot(message: str, opportunities: list[Any]) -> dict:
    """Process a copilot message and return answer + source metrics."""
    portfolio_names = [o.company_name for o in opportunities]
    companies = _extract_companies(message, portfolio_names)
    intent = _classify_intent(message, companies)

    contexts: list[CompanyContext] = []
    include_historical = _wants_historical(message)
    if intent not in ("portfolio_ranking", "portfolio_overview"):
        contexts = _load_contexts_parallel(companies, opportunities, include_historical)

    template_answer = _template_response(intent, contexts, opportunities)
    use_template = _should_use_template(intent, contexts, opportunities)

    if use_template:
        answer = template_answer
    else:
        context_payload = _build_context_payload(intent, contexts, opportunities)
        answer = await _generate_ai_answer(message, context_payload) or template_answer

    sources: list[dict] = []
    if intent == "risk_analysis":
        for ctx in contexts:
            sources.extend(_collect_risk_sources(ctx))
    elif intent in ("portfolio_ranking", "portfolio_overview"):
        for o in sorted(opportunities, key=lambda x: x.priority_score or 0, reverse=True)[:5]:
            sources.append({
                "label": "Priority Score",
                "value": f"{o.priority_score:.1f} (Inv {o.investment_score}, Risk {o.risk_score})",
                "company": o.company_name,
                "category": "Portfolio Data",
            })
    else:
        for ctx in contexts:
            sources.extend(_collect_company_sources(ctx))

    grounded = sorted({
        layer
        for ctx in contexts
        for layer in ctx.data_layers
    })
    if intent in ("portfolio_ranking", "portfolio_overview"):
        grounded.append("Portfolio Data")
    grounded = sorted(set(grounded))

    return {
        "answer": answer,
        "intent": intent,
        "companies": companies,
        "sources": sources[:20],
        "grounded_in": grounded or ["AcquiSight Platform Data"],
    }
