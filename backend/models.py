"""
Pydantic request / response models for AcquiSight AI.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


class Industry(str, Enum):
    SAAS = "SaaS"
    FINTECH = "Fintech"
    HEALTHCARE = "Healthcare"
    MANUFACTURING = "Manufacturing"
    CONSUMER = "Consumer"
    ENERGY = "Energy"
    REAL_ESTATE = "Real Estate"
    TECHNOLOGY = "Technology"
    RETAIL = "Retail"
    OTHER = "Other"


class DealScreenRequest(BaseModel):
    """Input payload for deal screening."""
    company_name: str = Field(..., min_length=1, max_length=200, example="Acme Corp")
    industry: Industry = Field(..., example="SaaS")
    revenue: float = Field(..., gt=0, description="Annual revenue in USD", example=50_000_000)
    ebitda: float = Field(..., description="EBITDA in USD (can be negative)", example=12_000_000)
    growth_rate: float = Field(..., description="YoY revenue growth rate %", example=28.0)
    debt: float = Field(..., ge=0, description="Total debt in USD", example=15_000_000)
    cash: float = Field(..., ge=0, description="Cash & equivalents in USD", example=8_000_000)
    country: str = Field(..., min_length=2, max_length=100, example="United States")

    @field_validator("revenue")
    @classmethod
    def revenue_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Revenue must be positive.")
        return v


class DimensionScores(BaseModel):
    """Breakdown of the five scoring dimensions."""
    growth: int
    profitability: int
    leverage: int
    revenue_quality: int
    financial_health: int


class CompData(BaseModel):
    """A single comparable company data point."""
    name: str
    ev_ebitda_multiple: float
    revenue_growth: Optional[float] = None
    ebitda_margin: Optional[float] = None


class CompsResult(BaseModel):
    """Comparable company analysis result."""
    companies: list[CompData]
    industry_avg_multiple: float
    estimated_ev: float
    ev_range_low: float
    ev_range_high: float


class DealScreenResponse(BaseModel):
    """Full deal screening response."""
    company_name: str
    industry: str
    # Calculated metrics
    ebitda_margin: float
    net_debt: float
    debt_to_ebitda: Optional[float]  # None if EBITDA <= 0
    enterprise_value: float
    # Scores (0–100)
    investment_score: int
    risk_score: int
    scores: DimensionScores
    # Recommendation
    recommendation: str
    recommendation_color: str  # hex colour for UI
    # Comps
    comps: CompsResult


class MemoRequest(BaseModel):
    """Request body for AI memo generation."""
    screen_result: DealScreenResponse
    analyst_notes: Optional[str] = Field(None, max_length=2000)


class MemoSection(BaseModel):
    title: str
    content: str


class MemoResponse(BaseModel):
    """Full AI-generated investment memo."""
    company_name: str
    sections: list[MemoSection]
    generated_at: str
