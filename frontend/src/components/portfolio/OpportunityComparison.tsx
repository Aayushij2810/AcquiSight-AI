import React, { useState } from 'react';
import { PortfolioOpportunity } from '../../types';
import { fmt } from '../../utils';

interface Props { opportunities: PortfolioOpportunity[] }

const METRICS: { key: string; label: string; higherBetter: boolean; fmt: (o: PortfolioOpportunity) => string; raw: (o: PortfolioOpportunity) => number }[] = [
  { key: 'revenue', label: 'Revenue', higherBetter: true, fmt: o => fmt.usdM(o.revenue), raw: o => o.revenue },
  { key: 'ebitda', label: 'EBITDA', higherBetter: true, fmt: o => fmt.usdM(o.ebitda), raw: o => o.ebitda },
  { key: 'growth', label: 'Growth Rate', higherBetter: true, fmt: o => fmt.pct(o.growth_rate), raw: o => o.growth_rate },
  { key: 'margin', label: 'EBITDA Margin', higherBetter: true, fmt: o => o.screen_result ? fmt.pct(o.screen_result.ebitda_margin) : '—', raw: o => o.screen_result?.ebitda_margin ?? 0 },
  { key: 'inv', label: 'Investment Score', higherBetter: true, fmt: o => `${o.investment_score}/100`, raw: o => o.investment_score },
  { key: 'risk', label: 'Risk Score', higherBetter: false, fmt: o => `${o.risk_score}/100`, raw: o => o.risk_score },
  { key: 'ev', label: 'Enterprise Value', higherBetter: true, fmt: o => fmt.usdM(o.enterprise_value), raw: o => o.enterprise_value },
];

export const OpportunityComparison: React.FC<Props> = ({ opportunities }) => {
  const [selected, setSelected] = useState<number[]>([]);

  const toggle = (id: number) => {
    setSelected(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : prev.length < 4 ? [...prev, id] : prev,
    );
  };

  const compared = opportunities.filter(o => selected.includes(o.id));

  const bestFor = (metric: typeof METRICS[0]) => {
    if (compared.length < 2) return null;
    const values = compared.map(o => ({ id: o.id, v: metric.raw(o) }));
    const best = metric.higherBetter
      ? values.reduce((a, b) => (b.v > a.v ? b : a))
      : values.reduce((a, b) => (b.v < a.v ? b : a));
    return best.id;
  };

  return (
    <div className="space-y-4">
      <div className="card">
        <p className="label mb-3">Select up to 4 companies to compare</p>
        <div className="flex flex-wrap gap-2">
          {opportunities.map(o => (
            <button
              key={o.id}
              type="button"
              onClick={() => toggle(o.id)}
              className={`px-3 py-1.5 rounded-lg text-xs border transition-colors ${
                selected.includes(o.id)
                  ? 'border-brand-400 bg-brand-500/15 text-brand-300'
                  : 'border-surface-border text-slate-400 hover:text-slate-200'
              }`}
            >
              {o.company_name}
            </button>
          ))}
        </div>
      </div>

      {compared.length >= 2 && (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                <th className="text-left py-2 px-3 label">Metric</th>
                {compared.map(o => (
                  <th key={o.id} className="text-left py-2 px-3 label">{o.company_name}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {METRICS.map(m => {
                const bestId = bestFor(m);
                return (
                  <tr key={m.key} className="border-b border-surface-border/50">
                    <td className="py-2 px-3 text-slate-400">{m.label}</td>
                    {compared.map(o => (
                      <td
                        key={o.id}
                        className={`py-2 px-3 font-mono tabular-nums ${
                          bestId === o.id ? 'text-green-400 font-semibold bg-green-500/5' : 'text-slate-200'
                        }`}
                      >
                        {m.fmt(o)}
                        {bestId === o.id && ' ✓'}
                      </td>
                    ))}
                  </tr>
                );
              })}
              <tr>
                <td className="py-2 px-3 text-slate-400">Recommendation</td>
                {compared.map(o => (
                  <td key={o.id} className="py-2 px-3 text-xs text-slate-300">{o.recommendation}</td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
