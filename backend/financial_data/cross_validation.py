"""Cross-validation across financial data providers."""

from __future__ import annotations

from dataclasses import dataclass

from financial_data.base import CompanyFinancialSnapshot, ProviderFetchResult

MATERIAL_THRESHOLD = 0.12  # 12% relative difference


@dataclass
class FieldDiscrepancy:
    field: str
    values: dict[str, float]
    max_difference_pct: float


@dataclass
class CrossValidationResult:
    flagged: bool
    message: str
    discrepancies: list[FieldDiscrepancy]
    providers_compared: list[str]


def cross_validate(results: list[ProviderFetchResult]) -> CrossValidationResult | None:
    successful = [r for r in results if r.data]
    if len(successful) < 2:
        return None

    discrepancies: list[FieldDiscrepancy] = []
    fields = ("revenue", "ebitda", "market_cap", "debt", "cash")

    for field in fields:
        values: dict[str, float] = {}
        for r in successful:
            val = getattr(r.data, field, None)
            if val is not None and val > 0:
                values[r.provider_label] = float(val)

        if len(values) < 2:
            continue

        nums = list(values.values())
        avg = sum(nums) / len(nums)
        if avg <= 0:
            continue
        max_diff = max(abs(v - avg) / avg for v in nums)
        if max_diff >= MATERIAL_THRESHOLD:
            discrepancies.append(FieldDiscrepancy(
                field=field,
                values=values,
                max_difference_pct=round(max_diff * 100, 1),
            ))

    flagged = len(discrepancies) > 0
    message = (
        "Financial Data Discrepancy Detected"
        if flagged
        else "Cross-provider validation passed — material fields consistent."
    )

    return CrossValidationResult(
        flagged=flagged,
        message=message,
        discrepancies=discrepancies,
        providers_compared=[r.provider_label for r in successful],
    )
