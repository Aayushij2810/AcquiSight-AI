"""
AcquiSight AI — AI Investment Memo Generator
Generates a professional PE-style investment memorandum.
Imported by routers/memo.py via:
  from memo_generator import generate_memo
"""

import os
from datetime import datetime, timezone
from typing import Optional

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from models import DealScreenResponse, MemoResponse, MemoSection


def _is_valid_api_key(api_key: str | None) -> bool:
    if not api_key:
        return False
    normalized = api_key.strip()
    if normalized in {"", "sk-your-key-here"}:
        return False
    return normalized.startswith("sk-") and len(normalized) > 20


# ── PROMPT BUILDER ────────────────────────────────────────────────────────────

def _build_prompt(screen_result: DealScreenResponse, analyst_notes: Optional[str]) -> str:
    s = screen_result
    notes_block = f"\n\nAnalyst Notes:\n{analyst_notes}" if analyst_notes else ""
    comps_names = ", ".join(c.name for c in s.comps.companies[:3])

    return f"""You are a Senior Private Equity Analyst at a top-tier buyout fund.
Write a professional Investment Committee memorandum for the following acquisition target.
The memo must be data-driven, concise, and analytically rigorous — written for a sophisticated
financial audience. Reference specific numbers from the data provided.

## Company Data
- Company: {s.company_name}
- Industry: {s.industry}
- EBITDA Margin: {s.ebitda_margin:.1f}%
- Net Debt: ${s.net_debt:,.0f}
- Debt/EBITDA: {f"{s.debt_to_ebitda:.1f}x" if s.debt_to_ebitda else "N/A"}
- Enterprise Value: ${s.enterprise_value:,.0f} ({s.valuation.method_used})
- Investment Score: {s.investment_score}/100
- Risk Score: {s.risk_score}/100 ({s.risk_label})
- Recommendation: {s.recommendation}

## Valuation Methodology
- Method: {s.valuation.method_used}
- Formulas: {'; '.join(s.valuation.formulas_used)}

## Comparable Companies (peers: {comps_names})
- Bear / Base / Bull Multiples: {s.comps.bear_multiple:.1f}x / {s.comps.base_multiple:.1f}x / {s.comps.bull_multiple:.1f}x
- Bear Case EV: ${s.comps.ev_range_low:,.0f}
- Base Case EV: ${s.comps.estimated_ev:,.0f}
- Bull Case EV: ${s.comps.ev_range_high:,.0f}

## Score Breakdown (Weighted)
{chr(10).join(f'- {b.dimension}: {b.formula}' for b in s.score_breakdown)}

## Risk Drivers
{chr(10).join(f'- {f.name} ({f.severity}): {f.description}' for f in s.risk_factors[:5])}
{notes_block}

---

Write the memo with EXACTLY these seven sections. Use the exact markdown headings below:

## Executive Summary
## Investment Thesis
## Key Strengths
## Key Risks
## Value Creation Opportunities
## Recommended Next Steps
## Final Recommendation

Be specific. Use real numbers from the data above. Each section should be 3–6 sentences or
bullet points. Do not use generic language. Write as if this memo will go to an Investment
Committee today.""".strip()


# ── SECTION PARSER ────────────────────────────────────────────────────────────

def _parse_sections(raw_text: str) -> list[MemoSection]:
    """
    Parse GPT output into structured MemoSection objects.
    Splits on ## headings.
    """
    sections = []
    current_title = None
    current_lines: list[str] = []

    for line in raw_text.splitlines():
        if line.startswith("## "):
            if current_title:
                sections.append(MemoSection(
                    title=current_title,
                    content="\n".join(current_lines).strip(),
                ))
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_title:
        sections.append(MemoSection(
            title=current_title,
            content="\n".join(current_lines).strip(),
        ))

    return sections


# ── FALLBACK TEMPLATE ─────────────────────────────────────────────────────────

def _template_memo(screen_result: DealScreenResponse) -> MemoResponse:
    """
    Deterministic fallback memo — used when OPENAI_API_KEY is not set.
    Produces professional output without any API calls.
    """
    s = screen_result
    comps_names = ", ".join(c.name for c in s.comps.companies[:3])
    leverage_str = f"{s.debt_to_ebitda:.1f}x" if s.debt_to_ebitda else "minimal"

    high_score = s.investment_score >= 65
    rec_tone = (
        "presents a compelling acquisition opportunity with a clear value creation roadmap"
        if high_score
        else "requires additional diligence before capital commitment given the risk profile"
    )

    sections = [
        MemoSection(
            title="Executive Summary",
            content=(
                f"{s.company_name} is a {s.industry} business with an EBITDA margin of "
                f"{s.ebitda_margin:.1f}% and net debt of ${s.net_debt:,.0f}. "
                f"The business scores {s.investment_score}/100 on our Investment Attractiveness "
                f"framework and carries a Risk Score of {s.risk_score}/100. "
                f"Based on a blended EV analysis against {comps_names} and sector peers, "
                f"we estimate enterprise value in the range of "
                f"${s.comps.ev_range_low:,.0f}–${s.comps.ev_range_high:,.0f} "
                f"(base: ${s.enterprise_value:,.0f}). "
                f"Our recommendation is: **{s.recommendation}**."
            ),
        ),
        MemoSection(
            title="Investment Thesis",
            content=(
                f"{s.company_name} operates in the {s.industry} sector where comparable "
                f"companies trade at a median {s.comps.industry_avg_multiple:.1f}x EV/EBITDA. "
                f"The company's EBITDA margin of {s.ebitda_margin:.1f}% and leverage of "
                f"{leverage_str} Debt/EBITDA "
                f"{'provide a solid foundation for value creation through operational improvement and selective M&A' if high_score else 'signal near-term operational and financial risks that must be addressed prior to exit positioning'}. "
                f"With a Growth Score of {s.scores.growth}/100 and Financial Health Score of "
                f"{s.scores.financial_health}/100, the business "
                f"{'demonstrates the resilience and market positioning required for a successful buyout' if high_score else 'requires a focused 100-day plan to stabilise and improve core KPIs'}."
            ),
        ),
        MemoSection(
            title="Key Strengths",
            content="\n".join([
                f"- **Profitability**: EBITDA margin of {s.ebitda_margin:.1f}% (Score: {s.scores.profitability}/100)",
                f"- **Growth trajectory**: Growth Score of {s.scores.growth}/100 indicates demand momentum",
                f"- **Revenue quality**: Revenue Quality Score of {s.scores.revenue_quality}/100 reflects scale and sustainability",
                f"- **Financial health**: Financial Health Score of {s.scores.financial_health}/100 — balance sheet supports operational investment",
                f"- **Valuation**: Implied EV of ${s.comps.estimated_ev:,.0f} at {s.comps.industry_avg_multiple:.1f}x peer multiple — attractive entry relative to sector",
                f"- **Sector tailwinds**: {s.industry} sector dynamics support continued demand",
            ]),
        ),
        MemoSection(
            title="Key Risks",
            content="\n".join([
                f"- **Leverage**: Debt/EBITDA of {leverage_str} (Leverage Score: {s.scores.leverage}/100) — requires active management" if s.debt_to_ebitda and s.debt_to_ebitda > 3 else f"- **Leverage**: Conservative at {leverage_str} Debt/EBITDA — monitor covenant headroom in rising rate environment",
                f"- **Margin compression**: At {s.ebitda_margin:.1f}% EBITDA margin, limited buffer against cost inflation or revenue shortfall",
                f"- **Market risk**: Sector competition and macro headwinds could compress growth from current trajectory",
                f"- **Integration risk**: Post-acquisition value creation plan dependent on management retention and execution",
                f"- **Exit timing**: {s.industry} sector multiples are sensitive to rate cycles; exit window must be monitored",
            ]),
        ),
        MemoSection(
            title="Value Creation Opportunities",
            content="\n".join([
                f"- **Margin expansion**: Benchmarking against top-quartile {s.industry} peers suggests {max(0, 40 - s.ebitda_margin):.0f}ppt+ of EBITDA margin upside through procurement and pricing discipline",
                "- **Organic growth**: Cross-sell/upsell within existing customer base; international expansion into adjacent markets",
                "- **M&A / Buy-and-build**: Fragmented sector creates bolt-on opportunities at 6–8x EBITDA vs. platform exit multiple",
                "- **Digital transformation**: Investment in automation and data analytics to reduce costs and improve retention",
                "- **Working capital optimisation**: Improving cash conversion cycle to accelerate deleveraging",
            ]),
        ),
        MemoSection(
            title="Recommended Next Steps",
            content="\n".join([
                "1. **Management Presentation** (Week 1–2): Strategic roadmap, customer concentration, and key contract terms",
                "2. **Quality of Earnings** (Week 2–5): Normalised EBITDA adjustments; cash conversion analysis",
                "3. **Commercial Due Diligence** (Week 3–6): Independent market sizing; customer NPS survey; competitive mapping",
                "4. **Legal & Regulatory** (Week 4–7): IP ownership; regulatory compliance; litigation review",
                "5. **Management Incentivisation** (Week 5–8): Equity rollover structure; performance-linked incentive plan",
                f"6. **Indicative Offer** (Week 6): LOI at ${s.enterprise_value:,.0f} base-case EV, subject to confirmatory diligence",
            ]),
        ),
        MemoSection(
            title="Final Recommendation",
            content=(
                f"Based on our financial analysis, risk assessment, and comparable company "
                f"benchmarking, {s.company_name} {rec_tone}. "
                f"The business scores {s.investment_score}/100 on our Investment Attractiveness "
                f"framework against a {s.risk_score}/100 Risk Score. "
                f"We recommend: **{s.recommendation}**. "
                f"Subject to confirmatory due diligence, we propose proceeding to a "
                f"non-binding indicative offer at a base-case enterprise value of "
                f"**${s.enterprise_value:,.0f}** ({s.comps.industry_avg_multiple:.1f}x LTM EBITDA). "
                f"\n\n*Generated by AcquiSight AI. For informational purposes only — not investment advice.*"
            ),
        ),
    ]

    return MemoResponse(
        company_name=s.company_name,
        sections=sections,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


# ── PUBLIC API ────────────────────────────────────────────────────────────────

async def generate_memo(
    screen_result: DealScreenResponse,
    analyst_notes: Optional[str] = None,
) -> MemoResponse:
    """
    Generate an AI investment memo.
    Uses GPT-4o when OPENAI_API_KEY is set; falls back to deterministic template.

    Args:
        screen_result:  Full DealScreenResponse from the /screen endpoint
        analyst_notes:  Optional free-text notes from the analyst

    Returns:
        MemoResponse with structured sections and timestamp
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not _is_valid_api_key(api_key) or not OPENAI_AVAILABLE:
        return _template_memo(screen_result)

    client = AsyncOpenAI(api_key=api_key)
    prompt = _build_prompt(screen_result, analyst_notes)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Senior Private Equity Analyst writing Investment Committee "
                    "memoranda. Your writing is precise, analytical, and backed by data. "
                    "You avoid generic language and write for a sophisticated financial audience."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.35,
        max_tokens=2200,
    )

    raw = response.choices[0].message.content
    sections = _parse_sections(raw)

    # Fallback if parsing fails
    if not sections:
        return _template_memo(screen_result)

    return MemoResponse(
        company_name=screen_result.company_name,
        sections=sections,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
