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

export type AppView = 'dashboard' | 'screen' | 'portfolio' | 'settings';

export type PortfolioTab =
  | 'overview'
  | 'pipeline'
  | 'rankings'
  | 'watchlist'
  | 'analytics'
  | 'compare'
  | 'ic';

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
  screen_result?: DealScreenResponse | null;
  memo?: MemoResponse | null;
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
