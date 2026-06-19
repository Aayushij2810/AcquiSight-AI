"""AI-generated portfolio insights."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from portfolio import build_analytics

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def _is_valid_api_key(api_key: str | None) -> bool:
    if not api_key:
        return False
    normalized = api_key.strip()
    if normalized in {"", "sk-your-key-here"}:
        return False
    return normalized.startswith("sk-") and len(normalized) > 20


def _template_insights(analytics: dict, opportunities: list) -> tuple[str, list[str]]:
    total = analytics["total_opportunities"]
    if total == 0:
        return (
            "Your portfolio is empty. Screen companies and add them to build your deal pipeline.",
            ["Screen your first target and click Add to Portfolio."],
        )

    avg_inv = analytics["avg_investment_score"]
    avg_risk = analytics["avg_risk_score"]
    industries = analytics["industry_breakdown"]
    top_industry = max(industries, key=lambda x: x["count"]) if industries else {"industry": "N/A", "count": 0}
    pct = round(top_industry["count"] / total * 100)

    high_scorers = [o for o in opportunities if o.investment_score >= 90]
    low_risk = [o for o in opportunities if o.risk_score <= 25]

    summary = (
        f"Your portfolio currently contains {total} opportunities. "
        f"Average Investment Score is {avg_inv:.0f} with average Risk Score of {avg_risk:.0f}. "
        f"{top_industry['industry']} represents {pct}% of opportunities. "
    )
    if high_scorers:
        summary += (
            f"{len(high_scorers)} {'company' if len(high_scorers) == 1 else 'companies'} "
            f"score above 90 and should be prioritised for due diligence. "
        )
    if low_risk:
        summary += (
            f"{len(low_risk)} opportunities carry very low risk profiles suitable for accelerated review."
        )

    recs = []
    if high_scorers:
        names = ", ".join(o.company_name for o in high_scorers[:3])
        recs.append(f"Prioritise due diligence on high-scoring targets: {names}.")
    if analytics["highlights"]["safest_investment"]:
        s = analytics["highlights"]["safest_investment"]
        recs.append(f"Safest profile: {s['company_name']} (Risk {s['risk_score']}/100).")
    if analytics["highlights"]["highest_growth"]:
        g = analytics["highlights"]["highest_growth"]
        recs.append(f"Fastest growth: {g['company_name']} ({g['growth_rate']:.1f}% YoY).")
    stage_counts = {s["stage"]: s["count"] for s in analytics["stage_breakdown"]}
    if stage_counts.get("Sourced", 0) > 3:
        recs.append("Multiple sourced deals awaiting screening — advance top priority targets.")
    if not recs:
        recs.append("Continue building pipeline breadth across industries and risk profiles.")

    return summary, recs


async def generate_portfolio_insights(opportunities: list) -> tuple[str, list[str]]:
    analytics = build_analytics(opportunities)

    api_key = os.getenv("OPENAI_API_KEY")
    if not _is_valid_api_key(api_key) or not OPENAI_AVAILABLE:
        return _template_insights(analytics, opportunities)

    client = AsyncOpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    prompt = f"""You are a Senior PE Portfolio Manager. Analyse this deal pipeline and write:
1. A 3-4 sentence portfolio summary (data-driven).
2. Three actionable recommendations as bullet points.

Portfolio Analytics:
- Total opportunities: {analytics['total_opportunities']}
- Avg investment score: {analytics['avg_investment_score']}
- Avg risk score: {analytics['avg_risk_score']}
- Industries: {analytics['industry_breakdown']}
- Pipeline stages: {analytics['stage_breakdown']}
- Best opportunity: {analytics['highlights']['best_opportunity']}

Format:
SUMMARY:
<paragraph>

RECOMMENDATIONS:
- <rec 1>
- <rec 2>
- <rec 3>"""

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600,
        )
        raw = response.choices[0].message.content or ""
        parts = raw.split("RECOMMENDATIONS:")
        summary = parts[0].replace("SUMMARY:", "").strip()
        recs = [
            line.lstrip("- ").strip()
            for line in parts[1].strip().split("\n")
            if line.strip().startswith("-")
        ] if len(parts) > 1 else []
        if not summary:
            return _template_insights(analytics, opportunities)
        return summary, recs or _template_insights(analytics, opportunities)[1]
    except Exception:
        return _template_insights(analytics, opportunities)
