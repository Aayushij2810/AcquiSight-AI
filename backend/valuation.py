"""
AcquiSight AI — Valuation Engine

Uses ONE methodology per deal (never blended):
  • Market-Based:        EV = Market Cap + Total Debt − Cash
  • Comparable Company:  EV = EBITDA × Industry EV/EBITDA Multiple
"""

from __future__ import annotations

from models import ValuationMethodology


def _fmt_usd(value: float) -> str:
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value:,.0f}"


def compute_enterprise_value(
    ebitda: float,
    debt: float,
    cash: float,
    industry: str,
    market_cap: float | None = None,
    base_multiple: float | None = None,
) -> ValuationMethodology:
    """
    Return enterprise value using a single, disclosed methodology.
    """
    if market_cap is not None and market_cap > 0:
        ev = market_cap + debt - cash
        return ValuationMethodology(
            method_used="Market-Based Valuation",
            enterprise_value=round(ev, 2),
            inputs_used=[
                f"Market Capitalization: {_fmt_usd(market_cap)}",
                f"Total Debt: {_fmt_usd(debt)}",
                f"Cash & Equivalents: {_fmt_usd(cash)}",
            ],
            multiples_used=["N/A — market price observed directly"],
            formulas_used=[
                "EV = Equity Value (Market Cap) + Total Debt − Cash",
                f"EV = {_fmt_usd(market_cap)} + {_fmt_usd(debt)} − {_fmt_usd(cash)} = {_fmt_usd(ev)}",
            ],
            assumptions_used=[
                "Public market capitalization reflects current equity value.",
                "Debt and cash are per the latest reported balance sheet.",
                "No control premium or minority discount applied.",
            ],
        )

    if ebitda <= 0:
        raise ValueError("EBITDA must be positive for comparable-company valuation.")

    multiple = base_multiple if base_multiple is not None else 10.0
    ev = ebitda * multiple

    return ValuationMethodology(
        method_used="Comparable Company Valuation",
        enterprise_value=round(ev, 2),
        inputs_used=[
            f"LTM EBITDA: {_fmt_usd(ebitda)}",
            f"Industry: {industry}",
            f"Peer Group Average EV/EBITDA: {multiple:.1f}x",
        ],
        multiples_used=[f"Base Case EV/EBITDA Multiple: {multiple:.1f}x"],
        formulas_used=[
            "EV = EBITDA × Industry EV/EBITDA Multiple",
            f"EV = {_fmt_usd(ebitda)} × {multiple:.1f}x = {_fmt_usd(ev)}",
        ],
        assumptions_used=[
            "Market capitalization unavailable; public trading comps used as proxy.",
            "Peer group reflects same-industry public companies (LTM multiples).",
            "Base case uses the arithmetic mean of peer EV/EBITDA multiples.",
            "No synergy, control, or liquidity adjustments applied.",
        ],
    )
