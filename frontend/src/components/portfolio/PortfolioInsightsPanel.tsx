import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';
import { fetchPortfolioInsights } from '../../api';
import { PortfolioInsights } from '../../types';

export const PortfolioInsightsPanel: React.FC = () => {
  const [insights, setInsights] = useState<PortfolioInsights | null>(null);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true);
    try {
      const data = await fetchPortfolioInsights();
      setInsights(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card border-brand-500/20 bg-brand-500/5 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Sparkles size={16} className="text-brand-400" />
            AI Portfolio Insights
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">Automated pipeline summary and prioritisation recommendations.</p>
        </div>
        <button type="button" className="btn-primary text-xs" onClick={generate} disabled={loading}>
          {loading ? 'Generating…' : 'Generate Insights'}
        </button>
      </div>
      {insights && (
        <>
          <p className="text-sm text-slate-300 leading-relaxed">{insights.summary}</p>
          <ul className="space-y-2">
            {insights.recommendations.map((r, i) => (
              <li key={i} className="text-xs text-slate-400 flex gap-2">
                <span className="text-brand-400">→</span> {r}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
};
