import React from 'react';
import { PortfolioOpportunity } from '../../types';
import { InvestmentTimingPanel } from '../InvestmentTimingPanel';
import { timingColor, fmt } from '../../utils';
import { Clock } from 'lucide-react';

interface Props { opportunities: PortfolioOpportunity[] }

export const PortfolioTimingView: React.FC<Props> = ({ opportunities }) => {
  const withTiming = opportunities.filter(o => o.timing || o.screen_result?.timing);

  if (withTiming.length === 0) {
    return (
      <div className="card text-center py-12 text-slate-500 text-sm">
        No timing data yet. Re-screen companies and add them to the portfolio to populate timing analysis.
      </div>
    );
  }

  const sorted = [...withTiming].sort(
    (a, b) => (b.timing_score ?? 0) - (a.timing_score ?? 0),
  );

  return (
    <div className="space-y-6">
      <div className="card">
        <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
          <Clock size={16} className="text-brand-400" /> Pipeline Timing Overview
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                {['Company', 'Timing Score', 'Status', 'Best Quarter', 'Confidence', 'Entry Assessment', 'EV'].map(h => (
                  <th key={h} className="text-left py-2 px-3 label">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sorted.map(o => {
                const t = o.timing || o.screen_result?.timing;
                return (
                  <tr key={o.id} className="border-b border-surface-border/50">
                    <td className="py-2 px-3 font-medium text-slate-200">{o.company_name}</td>
                    <td className="py-2 px-3 font-mono" style={{ color: timingColor(o.timing_score ?? t?.timing_score ?? 0) }}>
                      {o.timing_score ?? t?.timing_score ?? '—'}
                    </td>
                    <td className="py-2 px-3 text-slate-400">{t?.status ?? '—'}</td>
                    <td className="py-2 px-3 text-slate-400">{o.best_quarter ?? t?.best_quarter ?? '—'}</td>
                    <td className="py-2 px-3 text-slate-500">{o.timing_confidence ?? t?.confidence_level ?? '—'}</td>
                    <td className="py-2 px-3 text-xs text-slate-500 max-w-[160px] truncate">
                      {o.entry_assessment ?? t?.entry_window_assessment ?? '—'}
                    </td>
                    <td className="py-2 px-3 tabular-nums">{fmt.usdM(o.enterprise_value)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {sorted.slice(0, 3).map(o => {
        const t = o.timing || o.screen_result?.timing;
        if (!t) return null;
        return (
          <div key={o.id}>
            <p className="text-xs text-slate-500 mb-2 uppercase tracking-wide">{o.company_name}</p>
            <InvestmentTimingPanel timing={t} />
          </div>
        );
      })}
    </div>
  );
};
