"""Map external sector/industry strings to AcquiSight Industry enum values."""

from __future__ import annotations

INDUSTRY_KEYWORDS: list[tuple[str, str]] = [
    ("software", "SaaS"),
    ("saas", "SaaS"),
    ("cloud", "SaaS"),
    ("internet content", "Technology"),
    ("semiconductor", "Technology"),
    ("technology", "Technology"),
    ("communication", "Telecommunications"),
    ("telecom", "Telecommunications"),
    ("fintech", "Fintech"),
    ("financial", "Fintech"),
    ("bank", "Fintech"),
    ("insurance", "Insurance"),
    ("health", "Healthcare"),
    ("biotech", "Pharmaceuticals & Biotech"),
    ("pharma", "Pharmaceuticals & Biotech"),
    ("drug", "Pharmaceuticals & Biotech"),
    ("manufactur", "Manufacturing"),
    ("industrial", "Industrial Services"),
    ("consumer cycl", "Consumer"),
    ("consumer def", "Consumer"),
    ("retail", "Retail"),
    ("e-commerce", "E-Commerce"),
    ("energy", "Energy"),
    ("oil", "Energy"),
    ("real estate", "Real Estate"),
    ("reit", "Real Estate"),
    ("media", "Media & Entertainment"),
    ("entertainment", "Media & Entertainment"),
    ("transport", "Logistics & Transportation"),
    ("airline", "Logistics & Transportation"),
    ("auto", "Automotive"),
    ("aerospace", "Aerospace & Defense"),
    ("defense", "Aerospace & Defense"),
    ("education", "Education"),
    ("hotel", "Hospitality & Leisure"),
    ("restaurant", "Hospitality & Leisure"),
    ("cyber", "Cybersecurity"),
    ("security software", "Cybersecurity"),
]


def map_industry(sector: str, industry: str, fallback: str = "Other") -> str:
    combined = f"{sector} {industry}".lower()
    for keyword, mapped in INDUSTRY_KEYWORDS:
        if keyword in combined:
            return mapped
    if sector:
        return map_industry("", sector, fallback)
    return fallback
