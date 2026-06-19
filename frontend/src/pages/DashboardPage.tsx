import React, { useEffect, useState } from 'react';
import { TrendingUp, Briefcase, ArrowRight } from 'lucide-react';
import { fetchPortfolio, fetchPortfolioAnalytics } from '../api';
import { PortfolioAnalytics, PortfolioOpportunity, AppView } from '../types';
import { PortfolioKPIs } from '../components/portfolio/PortfolioKPIs';
import { PortfolioInsightsPanel } from '../components/portfolio/PortfolioInsightsPanel';
import { fmt } from '../utils';

interface Props { onNavigate: (view: AppView) => void }

export const DashboardPage: React.FC<Props> = ({ onNavigate }) => {
  const [analytics, setAnalytics] = useState<PortfolioAnalytics | null>(null);
  const [recent, setRecent] = useState<PortfolioOpportunity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchPortfolioAnalytics(), fetchPortfolio({ sort_by: 'date_added' })])
      .then(([a, p]) => { setAnalytics(a); setRecent(p.slice(0, 5)); })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 fade-in-up">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">Dashboard</h1>
          <p className="text-sm text-slate-500 mt-1">Portfolio-level investment intelligence at a glance.</p>
        </div>
        <button type="button" className="btn-primary" onClick={() => onNavigate('portfolio')}>
          <Briefcase size={16} /> Open Portfolio Mode
        </button>
      </div>

      <PortfolioKPIs analytics={analytics} loading={loading} />

      {analytics && analytics.total_opportunities > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="card">
            <p className="label mb-2">Lowest Risk Opportunity</p>
            <p className="text-lg font-semibold text-slate-100">{analytics.lowest_risk?.company_name || '—'}</p>
            <p className="text-xs text-slate-500">Risk score {analytics.lowest_risk?.risk_score}/100</p>
          </div>
          <div className="card">
            <p className="label mb-2">Best Priority Score</p>
            <p className="text-lg font-semibold text-slate-100">{analytics.highlights.best_opportunity?.company_name || '—'}</p>
            <p className="text-xs text-slate-500">Priority {analytics.highlights.best_opportunity?.priority_score?.toFixed(1)}</p>
          </div>
        </div>
      )}

      <PortfolioInsightsPanel />

      {recent.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <TrendingUp size={16} className="text-brand-400" /> Recent Pipeline Activity
            </h3>
            <button type="button" className="text-xs text-brand-400 flex items-center gap-1" onClick={() => onNavigate('portfolio')}>
              View all <ArrowRight size={12} />
            </button>
          </div>
          <div className="space-y-2">
            {recent.map(o => (
              <div key={o.id} className="flex items-center justify-between bg-surface-raised rounded-lg px-3 py-2 text-sm">
                <span className="text-slate-200">{o.company_name}</span>
                <span className="text-slate-500 text-xs">{o.industry} · {fmt.usdM(o.enterprise_value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
