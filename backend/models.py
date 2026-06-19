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
    TELECOMMUNICATIONS = "Telecommunications"
    MEDIA_ENTERTAINMENT = "Media & Entertainment"
    LOGISTICS_TRANSPORTATION = "Logistics & Transportation"
    PHARMA_BIOTECH = "Pharmaceuticals & Biotech"
    INSURANCE = "Insurance"
    AUTOMOTIVE = "Automotive"
    AEROSPACE_DEFENSE = "Aerospace & Defense"
    EDUCATION = "Education"
    HOSPITALITY_LEISURE = "Hospitality & Leisure"
    CYBERSECURITY = "Cybersecurity"
    ECOMMERCE = "E-Commerce"
    INDUSTRIAL_SERVICES = "Industrial Services"
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
    market_cap: Optional[float] = Field(
        None,
        gt=0,
        description="Market capitalization in USD (public companies only)",
        example=None,
    )

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


class ScoreBreakdownItem(BaseModel):
    """Weighted contribution of one scoring dimension."""
    dimension: str
    raw_score: int
    weight_pct: float
    weighted_contribution: float
    formula: str


class CompData(BaseModel):
    """A single comparable company data point."""
    name: str
    ev_ebitda_multiple: float
    revenue_growth: Optional[float] = None
    ebitda_margin: Optional[float] = None


class ValuationCase(BaseModel):
    """Bear / base / bull EV scenario from comparable multiples."""
    label: str
    multiple: float
    enterprise_value: float
    calculation: str


class CompsResult(BaseModel):
    """Comparable company analysis result."""
    companies: list[CompData]
    bear_multiple: float
    base_multiple: float
    bull_multiple: float
    industry_avg_multiple: float
    estimated_ev: float
    ev_range_low: float
    ev_range_high: float
    cases: list[ValuationCase]


class ValuationMethodology(BaseModel):
    """Transparent valuation audit trail."""
    method_used: str
    enterprise_value: float
    inputs_used: list[str]
    multiples_used: list[str]
    formulas_used: list[str]
    assumptions_used: list[str]


class RiskFactor(BaseModel):
    """Identified risk driver with severity and mitigation."""
    category: str
    name: str
    severity: str
    description: str
    mitigation: str


class RiskBreakdownItem(BaseModel):
    """Weighted contribution of one risk dimension."""
    dimension: str
    sub_score: float
    weight_pct: float
    weighted_contribution: float


class QuarterAttractiveness(BaseModel):
    quarter: str
    attractiveness_score: int
    outlook: str


class TimingCatalyst(BaseModel):
    category: str
    name: str
    description: str


class TimingAnalysis(BaseModel):
    """Investment Timing Engine output — analytical research, not advice."""
    timing_score: int
    status: str
    entry_window_assessment: str
    entry_window_reasons: list[str]
    quarter_analysis: list[QuarterAttractiveness]
    best_quarter: str
    positive_catalysts: list[TimingCatalyst]
    risk_catalysts: list[TimingCatalyst]
    confidence_level: str
    confidence_score: float
    analyst_commentary: str
    industry_timing_factors: list[str]
    disclaimer: str
    score_components: dict[str, float]


class DealScreenResponse(BaseModel):
    """Full deal screening response."""
    company_name: str
    industry: str
    ebitda_margin: float
    net_debt: float
    debt_to_ebitda: Optional[float]
    enterprise_value: float
    investment_score: int
    risk_score: int
    risk_label: str
    scores: DimensionScores
    score_breakdown: list[ScoreBreakdownItem]
    recommendation: str
    recommendation_color: str
    valuation: ValuationMethodology
    risk_factors: list[RiskFactor]
    risk_breakdown: list[RiskBreakdownItem]
    comps: CompsResult
    timing: TimingAnalysis


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


# ── Portfolio Mode ────────────────────────────────────────────────────────────

class PipelineStatus(str, Enum):
    SOURCED = "Sourced"
    SCREENING = "Screening"
    DUE_DILIGENCE = "Due Diligence"
    INVESTMENT_COMMITTEE = "Investment Committee"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class ICDecision(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class AddToPortfolioRequest(BaseModel):
    screen_result: DealScreenResponse
    revenue: float = Field(..., gt=0)
    ebitda: float
    growth_rate: float
    debt: float = Field(..., ge=0)
    cash: float = Field(..., ge=0)
    notes: Optional[str] = Field(None, max_length=5000)
    status: PipelineStatus = PipelineStatus.SCREENING
    watchlist: bool = False
    memo: Optional[MemoResponse] = None


class PortfolioUpdateRequest(BaseModel):
    status: Optional[PipelineStatus] = None
    notes: Optional[str] = Field(None, max_length=5000)
    watchlist: Optional[bool] = None
    ic_decision: Optional[ICDecision] = None


class PortfolioOpportunity(BaseModel):
    id: int
    company_name: str
    industry: str
    revenue: float
    ebitda: float
    growth_rate: float
    debt: float
    cash: float
    investment_score: int
    risk_score: int
    recommendation: str
    enterprise_value: float
    priority_score: float
    date_added: str
    status: str
    notes: str
    watchlist: bool
    ic_decision: str
    timing_score: Optional[int] = None
    best_quarter: Optional[str] = None
    timing_confidence: Optional[str] = None
    entry_assessment: Optional[str] = None
    screen_result: Optional[dict] = None
    memo: Optional[dict] = None
    timing: Optional[TimingAnalysis] = None


class PortfolioInsightsResponse(BaseModel):
    summary: str
    recommendations: list[str]
    generated_at: str


# ── Financial Data Layer ──────────────────────────────────────────────────────

class DataProvenance(BaseModel):
    data_source: str
    provider_id: str
    last_updated: str
    confidence: str
    reliability_score: int
    reliability_grade: str
    fallback_chain: list[str] = Field(default_factory=list)
    fiscal_period: Optional[str] = None
    data_freshness: str = "Live market data"


class CompanySearchMatch(BaseModel):
    ticker: str
    company_name: str
    exchange: str = ""
    match_type: str = "search"
    confidence: float = 0.75
    source: str = "combined"


class CompanySearchResponse(BaseModel):
    query: str
    results: list[CompanySearchMatch]


class CompanyResolutionInfo(BaseModel):
    match_type: str
    confidence: float
    source: str
    resolved_ticker: str
    resolved_name: str


class FieldDiscrepancy(BaseModel):
    field: str
    values: dict[str, float]
    max_difference_pct: float


class CrossValidationReport(BaseModel):
    flagged: bool
    message: str
    providers_compared: list[str]
    discrepancies: list[FieldDiscrepancy]


class ProviderAttempt(BaseModel):
    provider_id: str
    provider_label: str
    success: bool
    error: Optional[str] = None
    confidence: Optional[str] = None


class ProviderStatus(BaseModel):
    provider_id: str
    provider_label: str
    priority: int
    configured: bool
    quality_weight: float


class CompanyIntelligenceResponse(BaseModel):
    query: str
    ticker: str
    company_name: str
    industry: str
    sector: str
    country: str
    revenue: float
    ebitda: float
    net_income: Optional[float] = None
    cash: float
    debt: float
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    revenue_growth: float
    ebitda_margin: float
    ev_ebitda_multiple: Optional[float] = None
    historical_financials: list[dict] = Field(default_factory=list)
    earnings_dates: list[str] = Field(default_factory=list)
    consensus_estimates: dict = Field(default_factory=dict)
    comparable_companies: list[str] = Field(default_factory=list)
    provenance: DataProvenance
    resolution: Optional[CompanyResolutionInfo] = None
    cross_validation: Optional[CrossValidationReport] = None
    providers_attempted: list[ProviderAttempt]
    provider_status: list[ProviderStatus]

