export interface DimensionScores {
  growth:          number;
  profitability:   number;
  leverage:        number;
  revenue_quality: number;
  financial_health: number;
}

export interface ScoreBreakdownItem {
  dimension:             string;
  raw_score:             number;
  weight_pct:            number;
  weighted_contribution: number;
  formula:               string;
}

export interface CompData {
  name:              string;
  ev_ebitda_multiple: number;
  revenue_growth?:   number | null;
  ebitda_margin?:    number | null;
}

export interface ValuationCase {
  label:             string;
  multiple:          number;
  enterprise_value:  number;
  calculation:       string;
}

export interface CompsResult {
  companies:             CompData[];
  bear_multiple:         number;
  base_multiple:         number;
  bull_multiple:         number;
  industry_avg_multiple:   number;
  estimated_ev:          number;
  ev_range_low:          number;
  ev_range_high:          number;
  cases:                 ValuationCase[];
}

export interface ValuationMethodology {
  method_used:       string;
  enterprise_value:  number;
  inputs_used:       string[];
  multiples_used:    string[];
  formulas_used:     string[];
  assumptions_used:  string[];
}

export interface RiskFactor {
  category:    string;
  name:        string;
  severity:    string;
  description: string;
  mitigation:  string;
}

export interface RiskBreakdownItem {
  dimension:             string;
  sub_score:             number;
  weight_pct:            number;
  weighted_contribution: number;
}

export interface DealScreenResponse {
  company_name:          string;
  industry:              string;
  ebitda_margin:         number;
  net_debt:              number;
  debt_to_ebitda:        number | null;
  enterprise_value:      number;
  investment_score:      number;
  risk_score:            number;
  risk_label:            string;
  scores:                DimensionScores;
  score_breakdown:       ScoreBreakdownItem[];
  recommendation:        string;
  recommendation_color:  string;
  valuation:             ValuationMethodology;
  risk_factors:          RiskFactor[];
  risk_breakdown:        RiskBreakdownItem[];
  comps:                 CompsResult;
  timing:                TimingAnalysis;
}

export interface QuarterAttractiveness {
  quarter:               string;
  attractiveness_score:  number;
  outlook:               string;
}

export interface TimingCatalyst {
  category:    string;
  name:        string;
  description: string;
}

export interface TimingAnalysis {
  timing_score:            number;
  status:                  string;
  entry_window_assessment: string;
  entry_window_reasons:    string[];
  quarter_analysis:        QuarterAttractiveness[];
  best_quarter:            string;
  positive_catalysts:      TimingCatalyst[];
  risk_catalysts:          TimingCatalyst[];
  confidence_level:        string;
  confidence_score:        number;
  analyst_commentary:      string;
  industry_timing_factors: string[];
  disclaimer:              string;
  score_components:        Record<string, number>;
}

export interface MemoSection {
  title:   string;
  content: string;
}

export interface MemoResponse {
  company_name:  string;
  sections:      MemoSection[];
  generated_at:  string;
}

export interface ScreeningFormData {
  company_name: string;
  industry:     string;
  revenue:      string;
  ebitda:       string;
  growth_rate:  string;
  debt:         string;
  cash:         string;
  country:      string;
  market_cap:   string;
}

export const INDUSTRIES = [
  'SaaS',
  'Fintech',
  'Healthcare',
  'Manufacturing',
  'Consumer',
  'Energy',
  'Real Estate',
  'Technology',
  'Retail',
  'Telecommunications',
  'Media & Entertainment',
  'Logistics & Transportation',
  'Pharmaceuticals & Biotech',
  'Insurance',
  'Automotive',
  'Aerospace & Defense',
  'Education',
  'Hospitality & Leisure',
  'Cybersecurity',
  'E-Commerce',
  'Industrial Services',
  'Other',
] as const;

export type AppView = 'dashboard' | 'screen' | 'portfolio' | 'historical' | 'copilot' | 'settings';

export type PortfolioTab =
  | 'overview'
  | 'pipeline'
  | 'rankings'
  | 'watchlist'
  | 'analytics'
  | 'compare'
  | 'ic'
  | 'timing';

export const PIPELINE_STAGES = [
  'Sourced',
  'Screening',
  'Due Diligence',
  'Investment Committee',
  'Approved',
  'Rejected',
] as const;

export interface PortfolioOpportunity {
  id: number;
  company_name: string;
  industry: string;
  revenue: number;
  ebitda: number;
  growth_rate: number;
  debt: number;
  cash: number;
  investment_score: number;
  risk_score: number;
  recommendation: string;
  enterprise_value: number;
  priority_score: number;
  date_added: string;
  status: string;
  notes: string;
  watchlist: boolean;
  ic_decision: string;
  timing_score?: number | null;
  best_quarter?: string | null;
  timing_confidence?: string | null;
  entry_assessment?: string | null;
  screen_result?: DealScreenResponse | null;
  memo?: MemoResponse | null;
  timing?: TimingAnalysis | null;
}

export interface PortfolioHighlight {
  id: number;
  company_name: string;
  industry: string;
  investment_score: number;
  risk_score: number;
  growth_rate: number;
  enterprise_value: number;
  priority_score: number;
  recommendation: string;
  status: string;
}

export interface PortfolioAnalytics {
  total_opportunities: number;
  avg_investment_score: number;
  avg_risk_score: number;
  total_enterprise_value: number;
  highest_scoring: PortfolioHighlight | null;
  lowest_risk: PortfolioHighlight | null;
  industries_represented: number;
  industry_breakdown: { industry: string; count: number }[];
  stage_breakdown: { stage: string; count: number }[];
  investment_score_distribution: { label: string; count: number }[];
  risk_score_distribution: { label: string; count: number }[];
  ev_distribution: { label: string; count: number }[];
  growth_risk_scatter: {
    company_name: string;
    growth_rate: number;
    risk_score: number;
    investment_score: number;
  }[];
  highlights: {
    best_opportunity: PortfolioHighlight | null;
    most_undervalued: PortfolioHighlight | null;
    highest_growth: PortfolioHighlight | null;
    safest_investment: PortfolioHighlight | null;
  };
  watchlist_top_scores: PortfolioHighlight[];
  watchlist_lowest_risk: PortfolioHighlight[];
  watchlist_fastest_growth: PortfolioHighlight[];
  watchlist_count?: number;
}

export interface PortfolioInsights {
  summary: string;
  recommendations: string[];
  generated_at: string;
}

export interface AddToPortfolioPayload {
  screen_result: DealScreenResponse;
  revenue: number;
  ebitda: number;
  growth_rate: number;
  debt: number;
  cash: number;
  notes?: string;
  watchlist?: boolean;
  memo?: MemoResponse;
}

export interface DataProvenance {
  data_source: string;
  provider_id: string;
  last_updated: string;
  confidence: string;
  reliability_score: number;
  reliability_grade: string;
  fallback_chain: string[];
  fiscal_period?: string | null;
  data_freshness?: string;
}

export interface CompanySearchMatch {
  ticker: string;
  company_name: string;
  exchange: string;
  match_type: string;
  confidence: number;
  source: string;
}

export interface CompanySearchResponse {
  query: string;
  results: CompanySearchMatch[];
}

export interface CompanyResolutionInfo {
  match_type: string;
  confidence: number;
  source: string;
  resolved_ticker: string;
  resolved_name: string;
}

export interface CompanyLookupError {
  message: string;
  suggestions: CompanySearchMatch[];
}

export interface CrossValidationReport {
  flagged: boolean;
  message: string;
  providers_compared: string[];
  discrepancies: {
    field: string;
    values: Record<string, number>;
    max_difference_pct: number;
  }[];
}

export interface CompanyIntelligence {
  query: string;
  ticker: string;
  company_name: string;
  industry: string;
  sector: string;
  country: string;
  revenue: number;
  ebitda: number;
  net_income?: number | null;
  cash: number;
  debt: number;
  market_cap?: number | null;
  enterprise_value?: number | null;
  revenue_growth: number;
  ebitda_margin: number;
  ev_ebitda_multiple?: number | null;
  historical_financials: Record<string, unknown>[];
  earnings_dates: string[];
  consensus_estimates: Record<string, unknown>;
  comparable_companies: string[];
  provenance: DataProvenance;
  resolution?: CompanyResolutionInfo | null;
  cross_validation?: CrossValidationReport | null;
  providers_attempted: {
    provider_id: string;
    provider_label: string;
    success: boolean;
    error?: string | null;
    confidence?: string | null;
  }[];
}

export interface ProviderStatus {
  provider_id: string;
  provider_label: string;
  priority: number;
  configured: boolean;
  quality_weight: number;
}

export interface YearlyFinancialPoint {
  year: number;
  label: string;
  revenue?: number | null;
  ebitda?: number | null;
  revenue_growth?: number | null;
  stock_price?: number | null;
}

export interface HistoricalTrendMetrics {
  revenue_cagr?: number | null;
  ebitda_cagr?: number | null;
  growth_consistency_score: number;
  revenue_volatility: number;
  ebitda_volatility: number;
}

export interface HistoricalTrends {
  query: string;
  ticker: string;
  company_name: string;
  currency: string;
  data_source: string;
  period_label: string;
  years: YearlyFinancialPoint[];
  metrics: HistoricalTrendMetrics;
  last_updated: string;
}

export interface CopilotSourceMetric {
  label: string;
  value: string;
  company?: string | null;
  category: string;
}

export interface CopilotChatResponse {
  answer: string;
  intent: string;
  companies: string[];
  sources: CopilotSourceMetric[];
  grounded_in: string[];
}

export interface ProviderConnectionStatus {
  provider_id: string;
  provider_label: string;
  priority: number;
  quality_weight: number;
  category: 'enterprise' | 'public';
  connection_state: 'connected' | 'available' | 'not_connected';
  badge: string;
  subtitle: string;
  has_credentials: boolean;
  credential_env_var?: string | null;
  last_successful_refresh?: string | null;
}

export interface FallbackProviderStatus {
  provider_id: string;
  provider_label: string;
  status: 'ready' | 'awaiting_credentials' | 'not_connected';
}

export interface DataLayerStatus {
  active_provider: {
    provider_id?: string | null;
    provider_label: string;
  };
  last_successful_refresh?: string | null;
  last_query?: string | null;
  last_ticker?: string | null;
  demo_mode_enabled: boolean;
  demo_mode_note?: string | null;
  fallback_providers: FallbackProviderStatus[];
  providers: ProviderConnectionStatus[];
}
