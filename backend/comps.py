"""
AcquiSight AI — Comparable Company Analysis
Bear / Base / Bull EV = Min / Avg / Max peer multiple × EBITDA.
"""

from __future__ import annotations

from models import CompData, CompsResult, ValuationCase


def _fmt_usd(value: float) -> str:
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value:,.0f}"


PEERS: dict[str, list[dict]] = {
    "SaaS": [
        {"name": "Salesforce", "ev_ebitda_multiple": 24.1, "revenue_growth": 9.2, "ebitda_margin": 28.2},
        {"name": "HubSpot", "ev_ebitda_multiple": 31.4, "revenue_growth": 21.3, "ebitda_margin": 12.1},
        {"name": "Adobe", "ev_ebitda_multiple": 22.6, "revenue_growth": 10.8, "ebitda_margin": 35.8},
        {"name": "Workday", "ev_ebitda_multiple": 26.8, "revenue_growth": 17.2, "ebitda_margin": 22.3},
        {"name": "ServiceNow", "ev_ebitda_multiple": 34.2, "revenue_growth": 22.1, "ebitda_margin": 27.6},
    ],
    "Fintech": [
        {"name": "PayPal", "ev_ebitda_multiple": 14.2, "revenue_growth": 8.1, "ebitda_margin": 20.4},
        {"name": "Block", "ev_ebitda_multiple": 18.4, "revenue_growth": 14.2, "ebitda_margin": 15.6},
        {"name": "Wise", "ev_ebitda_multiple": 28.6, "revenue_growth": 31.0, "ebitda_margin": 24.5},
        {"name": "Adyen", "ev_ebitda_multiple": 31.2, "revenue_growth": 18.5, "ebitda_margin": 45.1},
        {"name": "Marqeta", "ev_ebitda_multiple": 20.8, "revenue_growth": 22.4, "ebitda_margin": 18.2},
    ],
    "Healthcare": [
        {"name": "UnitedHealth", "ev_ebitda_multiple": 13.4, "revenue_growth": 9.4, "ebitda_margin": 8.1},
        {"name": "Medtronic", "ev_ebitda_multiple": 12.1, "revenue_growth": 2.8, "ebitda_margin": 24.6},
        {"name": "Abbott Labs", "ev_ebitda_multiple": 15.8, "revenue_growth": 7.2, "ebitda_margin": 21.3},
        {"name": "Danaher", "ev_ebitda_multiple": 16.9, "revenue_growth": 4.1, "ebitda_margin": 27.4},
        {"name": "Intuitive Surgical", "ev_ebitda_multiple": 38.4, "revenue_growth": 14.8, "ebitda_margin": 32.5},
    ],
    "Manufacturing": [
        {"name": "Honeywell", "ev_ebitda_multiple": 14.2, "revenue_growth": 5.8, "ebitda_margin": 21.4},
        {"name": "Emerson Electric", "ev_ebitda_multiple": 13.6, "revenue_growth": 8.2, "ebitda_margin": 24.8},
        {"name": "Parker Hannifin", "ev_ebitda_multiple": 12.8, "revenue_growth": 9.4, "ebitda_margin": 22.6},
        {"name": "Illinois Tool Works", "ev_ebitda_multiple": 15.8, "revenue_growth": 2.4, "ebitda_margin": 26.4},
        {"name": "Roper Technologies", "ev_ebitda_multiple": 18.4, "revenue_growth": 12.6, "ebitda_margin": 35.1},
    ],
    "Consumer": [
        {"name": "Nike", "ev_ebitda_multiple": 17.4, "revenue_growth": 3.2, "ebitda_margin": 12.1},
        {"name": "Procter & Gamble", "ev_ebitda_multiple": 18.6, "revenue_growth": 3.8, "ebitda_margin": 22.8},
        {"name": "Unilever", "ev_ebitda_multiple": 11.2, "revenue_growth": 1.4, "ebitda_margin": 18.4},
        {"name": "L'Oréal", "ev_ebitda_multiple": 20.4, "revenue_growth": 10.2, "ebitda_margin": 21.6},
        {"name": "Reckitt", "ev_ebitda_multiple": 12.8, "revenue_growth": 2.8, "ebitda_margin": 26.4},
    ],
    "Energy": [
        {"name": "ExxonMobil", "ev_ebitda_multiple": 6.4, "revenue_growth": 7.8, "ebitda_margin": 18.6},
        {"name": "Chevron", "ev_ebitda_multiple": 5.8, "revenue_growth": 4.1, "ebitda_margin": 16.2},
        {"name": "NextEra Energy", "ev_ebitda_multiple": 12.8, "revenue_growth": 14.2, "ebitda_margin": 38.4},
        {"name": "BP", "ev_ebitda_multiple": 5.2, "revenue_growth": 2.8, "ebitda_margin": 9.4},
        {"name": "Enbridge", "ev_ebitda_multiple": 14.6, "revenue_growth": 6.4, "ebitda_margin": 42.1},
    ],
    "Real Estate": [
        {"name": "Prologis", "ev_ebitda_multiple": 22.4, "revenue_growth": 12.1, "ebitda_margin": 64.2},
        {"name": "CBRE Group", "ev_ebitda_multiple": 14.8, "revenue_growth": 8.4, "ebitda_margin": 8.6},
        {"name": "Welltower", "ev_ebitda_multiple": 18.6, "revenue_growth": 14.2, "ebitda_margin": 28.4},
        {"name": "AvalonBay", "ev_ebitda_multiple": 20.1, "revenue_growth": 6.8, "ebitda_margin": 54.6},
        {"name": "Simon Property", "ev_ebitda_multiple": 12.4, "revenue_growth": 4.2, "ebitda_margin": 58.8},
    ],
    "Technology": [
        {"name": "Microsoft", "ev_ebitda_multiple": 26.8, "revenue_growth": 15.2, "ebitda_margin": 41.2},
        {"name": "Alphabet", "ev_ebitda_multiple": 21.4, "revenue_growth": 10.8, "ebitda_margin": 30.1},
        {"name": "Meta", "ev_ebitda_multiple": 19.8, "revenue_growth": 21.4, "ebitda_margin": 38.6},
        {"name": "Snowflake", "ev_ebitda_multiple": 28.4, "revenue_growth": 32.1, "ebitda_margin": 5.2},
        {"name": "Datadog", "ev_ebitda_multiple": 35.2, "revenue_growth": 26.4, "ebitda_margin": 18.6},
    ],
    "Retail": [
        {"name": "Amazon (Retail)", "ev_ebitda_multiple": 14.2, "revenue_growth": 11.4, "ebitda_margin": 6.8},
        {"name": "Walmart", "ev_ebitda_multiple": 13.6, "revenue_growth": 5.2, "ebitda_margin": 5.4},
        {"name": "Costco", "ev_ebitda_multiple": 18.4, "revenue_growth": 8.6, "ebitda_margin": 6.2},
        {"name": "Target", "ev_ebitda_multiple": 10.8, "revenue_growth": 2.4, "ebitda_margin": 7.8},
        {"name": "Dollar General", "ev_ebitda_multiple": 11.4, "revenue_growth": 4.8, "ebitda_margin": 11.2},
    ],
    "Other": [
        {"name": "Visa", "ev_ebitda_multiple": 24.8, "revenue_growth": 10.2, "ebitda_margin": 62.4},
        {"name": "Mastercard", "ev_ebitda_multiple": 26.2, "revenue_growth": 11.4, "ebitda_margin": 54.6},
        {"name": "Berkshire Hathaway", "ev_ebitda_multiple": 11.4, "revenue_growth": 6.2, "ebitda_margin": 12.6},
        {"name": "3M", "ev_ebitda_multiple": 9.8, "revenue_growth": -0.8, "ebitda_margin": 16.4},
        {"name": "Honeywell", "ev_ebitda_multiple": 14.2, "revenue_growth": 5.8, "ebitda_margin": 21.4},
    ],
    "Telecommunications": [
        {"name": "Verizon", "ev_ebitda_multiple": 7.8, "revenue_growth": 0.6, "ebitda_margin": 24.8},
        {"name": "AT&T", "ev_ebitda_multiple": 6.4, "revenue_growth": 1.2, "ebitda_margin": 28.4},
        {"name": "T-Mobile", "ev_ebitda_multiple": 9.2, "revenue_growth": 4.8, "ebitda_margin": 32.1},
        {"name": "Comcast", "ev_ebitda_multiple": 8.6, "revenue_growth": 2.4, "ebitda_margin": 22.6},
        {"name": "Deutsche Telekom", "ev_ebitda_multiple": 7.2, "revenue_growth": 3.1, "ebitda_margin": 26.4},
    ],
    "Media & Entertainment": [
        {"name": "Disney", "ev_ebitda_multiple": 12.4, "revenue_growth": 3.8, "ebitda_margin": 18.2},
        {"name": "Netflix", "ev_ebitda_multiple": 18.6, "revenue_growth": 12.4, "ebitda_margin": 22.8},
        {"name": "Warner Bros. Discovery", "ev_ebitda_multiple": 8.2, "revenue_growth": -2.1, "ebitda_margin": 24.6},
        {"name": "Spotify", "ev_ebitda_multiple": 22.4, "revenue_growth": 18.2, "ebitda_margin": 8.4},
        {"name": "Live Nation", "ev_ebitda_multiple": 14.8, "revenue_growth": 11.6, "ebitda_margin": 12.8},
    ],
    "Logistics & Transportation": [
        {"name": "FedEx", "ev_ebitda_multiple": 9.8, "revenue_growth": 2.4, "ebitda_margin": 11.2},
        {"name": "UPS", "ev_ebitda_multiple": 10.4, "revenue_growth": 1.8, "ebitda_margin": 14.6},
        {"name": "Union Pacific", "ev_ebitda_multiple": 12.8, "revenue_growth": 4.2, "ebitda_margin": 38.4},
        {"name": "Maersk", "ev_ebitda_multiple": 6.2, "revenue_growth": -8.4, "ebitda_margin": 18.6},
        {"name": "DHL Group", "ev_ebitda_multiple": 8.4, "revenue_growth": 3.6, "ebitda_margin": 10.8},
    ],
    "Pharmaceuticals & Biotech": [
        {"name": "Pfizer", "ev_ebitda_multiple": 9.4, "revenue_growth": -2.8, "ebitda_margin": 28.4},
        {"name": "Johnson & Johnson", "ev_ebitda_multiple": 14.2, "revenue_growth": 4.6, "ebitda_margin": 32.8},
        {"name": "Merck", "ev_ebitda_multiple": 12.8, "revenue_growth": 6.2, "ebitda_margin": 34.2},
        {"name": "AbbVie", "ev_ebitda_multiple": 11.6, "revenue_growth": 3.4, "ebitda_margin": 42.6},
        {"name": "Amgen", "ev_ebitda_multiple": 13.4, "revenue_growth": 5.8, "ebitda_margin": 38.4},
    ],
    "Insurance": [
        {"name": "Berkshire Hathaway", "ev_ebitda_multiple": 11.4, "revenue_growth": 6.2, "ebitda_margin": 12.6},
        {"name": "UnitedHealth", "ev_ebitda_multiple": 13.4, "revenue_growth": 9.4, "ebitda_margin": 8.1},
        {"name": "Progressive", "ev_ebitda_multiple": 10.8, "revenue_growth": 18.4, "ebitda_margin": 14.2},
        {"name": "Allianz", "ev_ebitda_multiple": 8.6, "revenue_growth": 4.8, "ebitda_margin": 11.4},
        {"name": "AIA Group", "ev_ebitda_multiple": 12.2, "revenue_growth": 8.2, "ebitda_margin": 18.6},
    ],
    "Automotive": [
        {"name": "Toyota", "ev_ebitda_multiple": 9.8, "revenue_growth": 8.4, "ebitda_margin": 12.4},
        {"name": "Ford", "ev_ebitda_multiple": 7.2, "revenue_growth": 4.2, "ebitda_margin": 8.6},
        {"name": "General Motors", "ev_ebitda_multiple": 6.8, "revenue_growth": 3.8, "ebitda_margin": 9.4},
        {"name": "Tesla", "ev_ebitda_multiple": 28.4, "revenue_growth": 18.6, "ebitda_margin": 14.8},
        {"name": "BMW", "ev_ebitda_multiple": 5.4, "revenue_growth": 2.6, "ebitda_margin": 11.2},
    ],
    "Aerospace & Defense": [
        {"name": "Lockheed Martin", "ev_ebitda_multiple": 14.8, "revenue_growth": 4.2, "ebitda_margin": 14.6},
        {"name": "RTX", "ev_ebitda_multiple": 12.4, "revenue_growth": 6.8, "ebitda_margin": 16.2},
        {"name": "Boeing", "ev_ebitda_multiple": 18.6, "revenue_growth": 8.4, "ebitda_margin": 4.8},
        {"name": "Northrop Grumman", "ev_ebitda_multiple": 13.6, "revenue_growth": 3.4, "ebitda_margin": 12.8},
        {"name": "Airbus", "ev_ebitda_multiple": 11.2, "revenue_growth": 9.6, "ebitda_margin": 10.4},
    ],
    "Education": [
        {"name": "Chegg", "ev_ebitda_multiple": 8.4, "revenue_growth": -12.4, "ebitda_margin": 18.2},
        {"name": "Pearson", "ev_ebitda_multiple": 10.2, "revenue_growth": 2.8, "ebitda_margin": 14.6},
        {"name": "Grand Canyon Education", "ev_ebitda_multiple": 12.8, "revenue_growth": 8.4, "ebitda_margin": 22.4},
        {"name": "Strategic Education", "ev_ebitda_multiple": 9.6, "revenue_growth": 4.2, "ebitda_margin": 18.8},
        {"name": "Duolingo", "ev_ebitda_multiple": 32.4, "revenue_growth": 38.2, "ebitda_margin": 12.6},
    ],
    "Hospitality & Leisure": [
        {"name": "Marriott", "ev_ebitda_multiple": 16.4, "revenue_growth": 8.2, "ebitda_margin": 18.6},
        {"name": "Hilton", "ev_ebitda_multiple": 18.2, "revenue_growth": 9.4, "ebitda_margin": 38.4},
        {"name": "Booking Holdings", "ev_ebitda_multiple": 14.8, "revenue_growth": 12.6, "ebitda_margin": 32.8},
        {"name": "Las Vegas Sands", "ev_ebitda_multiple": 12.4, "revenue_growth": 14.2, "ebitda_margin": 34.2},
        {"name": "Carnival", "ev_ebitda_multiple": 8.6, "revenue_growth": 18.4, "ebitda_margin": 28.4},
    ],
    "Cybersecurity": [
        {"name": "Palo Alto Networks", "ev_ebitda_multiple": 38.4, "revenue_growth": 18.2, "ebitda_margin": 18.6},
        {"name": "CrowdStrike", "ev_ebitda_multiple": 42.8, "revenue_growth": 32.4, "ebitda_margin": 12.4},
        {"name": "Fortinet", "ev_ebitda_multiple": 28.6, "revenue_growth": 22.8, "ebitda_margin": 28.4},
        {"name": "Zscaler", "ev_ebitda_multiple": 36.2, "revenue_growth": 28.4, "ebitda_margin": 8.2},
        {"name": "Okta", "ev_ebitda_multiple": 24.8, "revenue_growth": 14.6, "ebitda_margin": 6.4},
    ],
    "E-Commerce": [
        {"name": "Amazon", "ev_ebitda_multiple": 18.4, "revenue_growth": 11.4, "ebitda_margin": 12.8},
        {"name": "Shopify", "ev_ebitda_multiple": 42.6, "revenue_growth": 24.2, "ebitda_margin": 14.2},
        {"name": "eBay", "ev_ebitda_multiple": 9.8, "revenue_growth": 2.4, "ebitda_margin": 28.6},
        {"name": "Etsy", "ev_ebitda_multiple": 16.4, "revenue_growth": 8.6, "ebitda_margin": 22.4},
        {"name": "MercadoLibre", "ev_ebitda_multiple": 28.2, "revenue_growth": 32.4, "ebitda_margin": 18.4},
    ],
    "Industrial Services": [
        {"name": "Cintas", "ev_ebitda_multiple": 18.6, "revenue_growth": 8.4, "ebitda_margin": 24.2},
        {"name": "Republic Services", "ev_ebitda_multiple": 14.2, "revenue_growth": 6.8, "ebitda_margin": 28.4},
        {"name": "Waste Management", "ev_ebitda_multiple": 15.8, "revenue_growth": 5.2, "ebitda_margin": 26.8},
        {"name": "Rollins", "ev_ebitda_multiple": 22.4, "revenue_growth": 10.2, "ebitda_margin": 22.6},
        {"name": "Stericycle", "ev_ebitda_multiple": 11.4, "revenue_growth": 3.8, "ebitda_margin": 18.4},
    ],
}


def get_comps(industry: str, ebitda: float) -> CompsResult:
    """Build peer comps with min / avg / max multiple scenarios."""
    peer_list = PEERS.get(industry, PEERS["Other"])
    multiples = [p["ev_ebitda_multiple"] for p in peer_list]

    bear_multiple = min(multiples)
    bull_multiple = max(multiples)
    base_multiple = round(sum(multiples) / len(multiples), 1)

    companies = [
        CompData(
            name=p["name"],
            ev_ebitda_multiple=p["ev_ebitda_multiple"],
            revenue_growth=p.get("revenue_growth"),
            ebitda_margin=p.get("ebitda_margin"),
        )
        for p in peer_list
    ]

    ebitda_label = _fmt_usd(ebitda)
    bear_ev = round(ebitda * bear_multiple, 2)
    base_ev = round(ebitda * base_multiple, 2)
    bull_ev = round(ebitda * bull_multiple, 2)

    cases = [
        ValuationCase(
            label="Bear Case EV",
            multiple=bear_multiple,
            enterprise_value=bear_ev,
            calculation=f"{bear_multiple:.1f}x × {ebitda_label} = {_fmt_usd(bear_ev)}",
        ),
        ValuationCase(
            label="Base Case EV",
            multiple=base_multiple,
            enterprise_value=base_ev,
            calculation=f"{base_multiple:.1f}x × {ebitda_label} = {_fmt_usd(base_ev)}",
        ),
        ValuationCase(
            label="Bull Case EV",
            multiple=bull_multiple,
            enterprise_value=bull_ev,
            calculation=f"{bull_multiple:.1f}x × {ebitda_label} = {_fmt_usd(bull_ev)}",
        ),
    ]

    return CompsResult(
        companies=companies,
        bear_multiple=bear_multiple,
        base_multiple=base_multiple,
        bull_multiple=bull_multiple,
        industry_avg_multiple=base_multiple,
        estimated_ev=base_ev,
        ev_range_low=bear_ev,
        ev_range_high=bull_ev,
        cases=cases,
    )
