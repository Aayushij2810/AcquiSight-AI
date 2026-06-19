export interface DimensionScores {
  growth:          number;
  profitability:   number;
  leverage:        number;
  revenue_quality: number;
  financial_health: number;
}

export interface CompData {
  name:              string;
  ev_ebitda_multiple: number;
  revenue_growth?:   number | null;
  ebitda_margin?:    number | null;
}

export interface CompsResult {
  companies:            CompData[];
  industry_avg_multiple: number;
  estimated_ev:         number;
  ev_range_low:         number;
  ev_range_high:        number;
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
  scores:                DimensionScores;
  recommendation:        string;
  recommendation_color:  string;
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
}
