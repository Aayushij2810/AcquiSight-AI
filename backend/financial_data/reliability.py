"""Data reliability scoring."""

from __future__ import annotations

from financial_data.base import CompanyFinancialSnapshot, ProviderFetchResult

INSTITUTIONAL_GRADE_THRESHOLD = 90
PUBLIC_SOURCE_THRESHOLD = 75

COMPARE_FIELDS = ("revenue", "ebitda", "market_cap", "debt", "cash")


def compute_reliability_score(
    primary: ProviderFetchResult,
    all_results: list[ProviderFetchResult],
    cross_validation_flagged: bool,
) -> tuple[int, str, str]:
    """
    Return (score 0-100, grade label, confidence High/Medium/Low).
    """
    if not primary.data:
        return 0, "No Data", "Low"

    base = primary.provider_quality_weight * 100

    # Field completeness (up to 15 pts)
    completeness = min(15, primary.fields_populated * 2)

    # Multi-source bonus (up to 10 pts)
    sources = sum(1 for r in all_results if r.data)
    multi_bonus = min(10, (sources - 1) * 5) if sources > 1 else 0

    # Consistency penalty
    consistency_penalty = 15 if cross_validation_flagged else 0

    # Recency — all fresh
    recency_bonus = 5

    score = int(round(min(100, max(0, base * 0.75 + completeness + multi_bonus + recency_bonus - consistency_penalty))))

    if score >= INSTITUTIONAL_GRADE_THRESHOLD:
        grade = "Institutional Grade Data"
        confidence = "High"
    elif score >= PUBLIC_SOURCE_THRESHOLD:
        grade = "Professional Market Data"
        confidence = "Medium"
    else:
        grade = "Public Source Data"
        confidence = "Low"

    if primary.provider_id in ("bloomberg", "factset", "capital_iq") and score >= 85:
        grade = "Institutional Grade Data"
        confidence = "High"

    return score, grade, confidence
