"""
AcquiSight AI — Comparable Company Analysis
Builds a peer group for the target company and calculates implied EV.
Imported by routers/screen.py via:
  from comps import get_comps
"""

from models import CompsResult, CompData


# ── PEER DATABASE ─────────────────────────────────────────────────────────────
# LTM data as of mid-2026. Amounts in USD.
# ev_ebitda_multiple: LTM EV/EBITDA
# revenue_growth:     YoY revenue growth %
# ebitda_margin:      LTM EBITDA margin %

PEERS: dict[str, list[dict]] = {
    "SaaS": [
        {"name": "Salesforce",    "ev_ebitda_multiple": 24.1, "revenue_growth": 9.2,  "ebitda_margin": 28.2},
        {"name": "HubSpot",       "ev_ebitda_multiple": 31.4, "revenue_growth": 21.3, "ebitda_margin": 12.1},
        {"name": "Adobe",         "ev_ebitda_multiple": 22.6, "revenue_growth": 10.8, "ebitda_margin": 35.8},
        {"name": "Workday",       "ev_ebitda_multiple": 26.8, "revenue_growth": 17.2, "ebitda_margin": 22.3},
        {"name": "ServiceNow",    "ev_ebitda_multiple": 34.2, "revenue_growth": 22.1, "ebitda_margin": 27.6},
    ],
    "Fintech": [
        {"name": "PayPal",        "ev_ebitda_multiple": 14.2, "revenue_growth": 8.1,  "ebitda_margin": 20.4},
        {"name": "Block",         "ev_ebitda_multiple": 18.4, "revenue_growth": 14.2, "ebitda_margin": 15.6},
        {"name": "Wise",          "ev_ebitda_multiple": 28.6, "revenue_growth": 31.0, "ebitda_margin": 24.5},
        {"name": "Adyen",         "ev_ebitda_multiple": 31.2, "revenue_growth": 18.5, "ebitda_margin": 45.1},
        {"name": "Marqeta",       "ev_ebitda_multiple": 20.8, "revenue_growth": 22.4, "ebitda_margin": 18.2},
    ],
    "Healthcare": [
        {"name": "UnitedHealth",   "ev_ebitda_multiple": 13.4, "revenue_growth": 9.4,  "ebitda_margin": 8.1},
        {"name": "Medtronic",      "ev_ebitda_multiple": 12.1, "revenue_growth": 2.8,  "ebitda_margin": 24.6},
        {"name": "Abbott Labs",    "ev_ebitda_multiple": 15.8, "revenue_growth": 7.2,  "ebitda_margin": 21.3},
        {"name": "Danaher",        "ev_ebitda_multiple": 16.9, "revenue_growth": 4.1,  "ebitda_margin": 27.4},
        {"name": "Intuitive Surgical", "ev_ebitda_multiple": 38.4, "revenue_growth": 14.8, "ebitda_margin": 32.5},
    ],
    "Manufacturing": [
        {"name": "Honeywell",      "ev_ebitda_multiple": 14.2, "revenue_growth": 5.8,  "ebitda_margin": 21.4},
        {"name": "Emerson Electric","ev_ebitda_multiple": 13.6, "revenue_growth": 8.2,  "ebitda_margin": 24.8},
        {"name": "Parker Hannifin","ev_ebitda_multiple": 12.8, "revenue_growth": 9.4,  "ebitda_margin": 22.6},
        {"name": "Illinois Tool Works","ev_ebitda_multiple": 15.8, "revenue_growth": 2.4, "ebitda_margin": 26.4},
        {"name": "Roper Technologies","ev_ebitda_multiple": 18.4, "revenue_growth": 12.6, "ebitda_margin": 35.1},
    ],
    "Consumer": [
        {"name": "Nike",           "ev_ebitda_multiple": 17.4, "revenue_growth": 3.2,  "ebitda_margin": 12.1},
        {"name": "Procter & Gamble","ev_ebitda_multiple": 18.6, "revenue_growth": 3.8,  "ebitda_margin": 22.8},
        {"name": "Unilever",       "ev_ebitda_multiple": 11.2, "revenue_growth": 1.4,  "ebitda_margin": 18.4},
        {"name": "L'Oréal",        "ev_ebitda_multiple": 20.4, "revenue_growth": 10.2, "ebitda_margin": 21.6},
        {"name": "Reckitt",        "ev_ebitda_multiple": 12.8, "revenue_growth": 2.8,  "ebitda_margin": 26.4},
    ],
    "Energy": [
        {"name": "ExxonMobil",     "ev_ebitda_multiple": 6.4,  "revenue_growth": 7.8,  "ebitda_margin": 18.6},
        {"name": "Chevron",        "ev_ebitda_multiple": 5.8,  "revenue_growth": 4.1,  "ebitda_margin": 16.2},
        {"name": "NextEra Energy", "ev_ebitda_multiple": 12.8, "revenue_growth": 14.2, "ebitda_margin": 38.4},
        {"name": "BP",             "ev_ebitda_multiple": 5.2,  "revenue_growth": 2.8,  "ebitda_margin": 9.4},
        {"name": "Enbridge",       "ev_ebitda_multiple": 14.6, "revenue_growth": 6.4,  "ebitda_margin": 42.1},
    ],
    "Real Estate": [
        {"name": "Prologis",       "ev_ebitda_multiple": 22.4, "revenue_growth": 12.1, "ebitda_margin": 64.2},
        {"name": "CBRE Group",     "ev_ebitda_multiple": 14.8, "revenue_growth": 8.4,  "ebitda_margin": 8.6},
        {"name": "Welltower",      "ev_ebitda_multiple": 18.6, "revenue_growth": 14.2, "ebitda_margin": 28.4},
        {"name": "AvalonBay",      "ev_ebitda_multiple": 20.1, "revenue_growth": 6.8,  "ebitda_margin": 54.6},
        {"name": "Simon Property", "ev_ebitda_multiple": 12.4, "revenue_growth": 4.2,  "ebitda_margin": 58.8},
    ],
    "Technology": [
        {"name": "Microsoft",      "ev_ebitda_multiple": 26.8, "revenue_growth": 15.2, "ebitda_margin": 41.2},
        {"name": "Alphabet",       "ev_ebitda_multiple": 21.4, "revenue_growth": 10.8, "ebitda_margin": 30.1},
        {"name": "Meta",           "ev_ebitda_multiple": 19.8, "revenue_growth": 21.4, "ebitda_margin": 38.6},
        {"name": "Snowflake",      "ev_ebitda_multiple": 28.4, "revenue_growth": 32.1, "ebitda_margin": 5.2},
        {"name": "Datadog",        "ev_ebitda_multiple": 35.2, "revenue_growth": 26.4, "ebitda_margin": 18.6},
    ],
    "Retail": [
        {"name": "Amazon (Retail)","ev_ebitda_multiple": 14.2, "revenue_growth": 11.4, "ebitda_margin": 6.8},
        {"name": "Walmart",        "ev_ebitda_multiple": 13.6, "revenue_growth": 5.2,  "ebitda_margin": 5.4},
        {"name": "Costco",         "ev_ebitda_multiple": 18.4, "revenue_growth": 8.6,  "ebitda_margin": 6.2},
        {"name": "Target",         "ev_ebitda_multiple": 10.8, "revenue_growth": 2.4,  "ebitda_margin": 7.8},
        {"name": "Dollar General", "ev_ebitda_multiple": 11.4, "revenue_growth": 4.8,  "ebitda_margin": 11.2},
    ],
    "Other": [
        {"name": "Visa",           "ev_ebitda_multiple": 24.8, "revenue_growth": 10.2, "ebitda_margin": 62.4},
        {"name": "Mastercard",     "ev_ebitda_multiple": 26.2, "revenue_growth": 11.4, "ebitda_margin": 54.6},
        {"name": "Berkshire Hathaway","ev_ebitda_multiple": 11.4, "revenue_growth": 6.2, "ebitda_margin": 12.6},
        {"name": "3M",             "ev_ebitda_multiple": 9.8,  "revenue_growth": -0.8, "ebitda_margin": 16.4},
        {"name": "Honeywell",      "ev_ebitda_multiple": 14.2, "revenue_growth": 5.8,  "ebitda_margin": 21.4},
    ],
}


def get_comps(industry: str, ebitda: float) -> CompsResult:
    """
    Build CompsResult for the given industry.

    Args:
        industry:  Industry string matching models.Industry enum values
        ebitda:    Subject company LTM EBITDA (USD)

    Returns:
        CompsResult with peer list, averages, and implied EV range
    """
    peer_list = PEERS.get(industry, PEERS["Other"])

    companies = [
        CompData(
            name=p["name"],
            ev_ebitda_multiple=p["ev_ebitda_multiple"],
            revenue_growth=p.get("revenue_growth"),
            ebitda_margin=p.get("ebitda_margin"),
        )
        for p in peer_list
    ]

    # Industry average multiple
    avg_multiple = round(
        sum(p["ev_ebitda_multiple"] for p in peer_list) / len(peer_list), 1
    )

    # Implied EV using average multiple
    estimated_ev = round(ebitda * avg_multiple, 2)

    # EV range: 25th pct multiple (bear) to 75th pct (bull)
    sorted_multiples = sorted(p["ev_ebitda_multiple"] for p in peer_list)
    low_multiple  = sorted_multiples[len(sorted_multiples) // 4]
    high_multiple = sorted_multiples[-(len(sorted_multiples) // 4 + 1)]

    return CompsResult(
        companies=companies,
        industry_avg_multiple=avg_multiple,
        estimated_ev=estimated_ev,
        ev_range_low=round(ebitda * low_multiple, 2),
        ev_range_high=round(ebitda * high_multiple, 2),
    )
