import React, { useCallback, useEffect, useState } from 'react';
import {
  fetchPortfolio, fetchPortfolioAnalytics, updatePortfolioOpportunity,
} from '../api';
import { PortfolioAnalytics, PortfolioOpportunity, PortfolioTab } from '../types';
import { PortfolioKPIs } from '../components/portfolio/PortfolioKPIs';
import { PipelineKanban } from '../components/portfolio/PipelineKanban';
import { PortfolioRanking } from '../components/portfolio/PortfolioRanking';
import { PortfolioWatchlist } from '../components/portfolio/PortfolioWatchlist';
import { PortfolioAnalyticsCharts } from '../components/portfolio/PortfolioAnalyticsCharts';
import { OpportunityComparison } from '../components/portfolio/OpportunityComparison';
import { InvestmentCommitteeView } from '../components/portfolio/InvestmentCommitteeView';
import { PortfolioInsightsPanel } from '../components/portfolio/PortfolioInsightsPanel';
import { PortfolioExport } from '../components/portfolio/PortfolioExport';
import { PortfolioTimingView } from '../components/portfolio/PortfolioTimingView';

const TABS: { id: PortfolioTab; label: string }[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'pipeline', label: 'Pipeline' },
  { id: 'rankings', label: 'Rankings' },
  { id: 'watchlist', label: 'Watchlist' },
  { id: 'analytics', label: 'Analytics' },
  { id: 'compare', label: 'Compare' },
  { id: 'ic', label: 'IC Review' },
  { id: 'timing', label: 'Timing' },
];

export const PortfolioPage: React.FC = () => {
  const [tab, setTab] = useState<PortfolioTab>('overview');
  const [opportunities, setOpportunities] = useState<PortfolioOpportunity[]>([]);
  const [analytics, setAnalytics] = useState<PortfolioAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [opps, a] = await Promise.all([fetchPortfolio(), fetchPortfolioAnalytics()]);
      setOpportunities(opps);
      setAnalytics(a);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleStatusChange = async (id: number, status: string) => {
    await updatePortfolioOpportunity(id, { status });
    load();
  };

  const handleWatchlist = async (id: number, watchlist: boolean) => {
    await updatePortfolioOpportunity(id, { watchlist });
    load();
  };

  const handleICDecision = async (id: number, ic_decision: 'Approved' | 'Rejected' | 'Pending') => {
    await updatePortfolioOpportunity(id, { ic_decision });
    load();
  };

  return (
    <div className="space-y-6 fade-in-up">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Portfolio Mode</h1>
        <p className="text-sm text-slate-500 mt-1">
          Track, Compare, Rank and Prioritise Investment Opportunities
        </p>
      </div>

      <div className="flex gap-1 overflow-x-auto border-b border-surface-border pb-px">
        {TABS.map(t => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
              tab === t.id ? 'border-brand-400 text-brand-300' : 'border-transparent text-slate-500 hover:text-slate-300'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'overview' && (
        <>
          <PortfolioKPIs analytics={analytics} loading={loading} />
          <PortfolioInsightsPanel />
          <PortfolioExport analytics={analytics} />
        </>
      )}

      {tab === 'pipeline' && (
        <PipelineKanban opportunities={opportunities} onStatusChange={handleStatusChange} />
      )}

      {tab === 'rankings' && <PortfolioRanking opportunities={opportunities} />}

      {tab === 'watchlist' && analytics && (
        <PortfolioWatchlist
          opportunities={opportunities}
          topScores={analytics.watchlist_top_scores}
          lowestRisk={analytics.watchlist_lowest_risk}
          fastestGrowth={analytics.watchlist_fastest_growth}
          onToggleWatchlist={handleWatchlist}
        />
      )}

      {tab === 'analytics' && <PortfolioAnalyticsCharts analytics={analytics} />}

      {tab === 'compare' && <OpportunityComparison opportunities={opportunities} />}

      {tab === 'ic' && (
        <InvestmentCommitteeView opportunities={opportunities} onDecision={handleICDecision} />
      )}

      {tab === 'timing' && <PortfolioTimingView opportunities={opportunities} />}
    </div>
  );
};
