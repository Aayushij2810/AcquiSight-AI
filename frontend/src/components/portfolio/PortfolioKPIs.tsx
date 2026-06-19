import React from 'react';
import { PortfolioAnalytics } from '../../types';
import { fmt } from '../../utils';

interface Props { analytics: PortfolioAnalytics | null; loading?: boolean }

const KPICard: React.FC<{ label: string; value: string; sub?: string }> = ({ label, value, sub }) => (
  <div className="card bg-surface-raised/50">
    <p className="label mb-2">{label}</p>
    <p className="text-xl font-semibold tabular-nums text-slate-100">{value}</p>
    {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
  </div>
);

export const PortfolioKPIs: React.FC<Props> = ({ analytics, loading }) => {
  if (loading || !analytics) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {[...Array(6)].map((_, i) => <div key={i} className="card skeleton h-20" />)}
      </div>
    );
  }

  if (analytics.total_opportunities === 0) {
    return (
      <div className="card text-center py-8 text-slate-500 text-sm">
        No opportunities in portfolio yet. Screen a company and click Add to Portfolio.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      <KPICard label="Total Opportunities" value={String(analytics.total_opportunities)} />
      <KPICard label="Avg Investment Score" value={`${analytics.avg_investment_score}`} sub="/ 100" />
      <KPICard label="Avg Risk Score" value={`${analytics.avg_risk_score}`} sub="/ 100" />
      <KPICard label="Total Enterprise Value" value={fmt.usdM(analytics.total_enterprise_value)} />
      <KPICard
        label="Highest Scoring"
        value={analytics.highest_scoring?.company_name || '—'}
        sub={analytics.highest_scoring ? `${analytics.highest_scoring.investment_score}/100` : undefined}
      />
      <KPICard label="Industries" value={String(analytics.industries_represented)} sub="represented" />
    </div>
  );
};
