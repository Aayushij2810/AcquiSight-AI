import React, { useMemo, useState } from 'react';
import { PortfolioOpportunity } from '../../types';
import { fmt, scoreColor, riskColor, timingColor } from '../../utils';
import { ArrowUpDown } from 'lucide-react';

type SortKey =
  | 'priority_score'
  | 'investment_score'
  | 'risk_score'
  | 'enterprise_value'
  | 'growth_rate'
  | 'date_added'
  | 'timing_score'
  | 'best_quarter';

interface Props { opportunities: PortfolioOpportunity[] }

export const PortfolioRanking: React.FC<Props> = ({ opportunities }) => {
  const [sortBy, setSortBy] = useState<SortKey>('priority_score');
  const [asc, setAsc] = useState(false);

  const sorted = useMemo(() => {
    const list = [...opportunities];
    list.sort((a, b) => {
      const av = (a[sortBy as keyof PortfolioOpportunity] ?? 0) as number | string;
      const bv = (b[sortBy as keyof PortfolioOpportunity] ?? 0) as number | string;
      if (typeof av === 'string') return asc ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
      return asc ? (av as number) - (bv as number) : (bv as number) - (av as number);
    });
    return list;
  }, [opportunities, sortBy, asc]);

  const toggleSort = (key: SortKey) => {
    if (sortBy === key) setAsc(!asc);
    else { setSortBy(key); setAsc(false); }
  };

  const Th: React.FC<{ k: SortKey; label: string }> = ({ k, label }) => (
    <th className="text-left py-2.5 px-3 label cursor-pointer hover:text-slate-300 whitespace-nowrap" onClick={() => toggleSort(k)}>
      <span className="inline-flex items-center gap-1">{label} <ArrowUpDown size={10} /></span>
    </th>
  );

  return (
    <div className="card overflow-x-auto">
      <h3 className="text-sm font-semibold text-slate-200 mb-4">Portfolio Ranking</h3>
      <table className="w-full text-sm min-w-[900px]">
        <thead>
          <tr className="border-b border-surface-border">
            <th className="text-left py-2.5 px-3 label">Rank</th>
            <th className="text-left py-2.5 px-3 label">Company</th>
            <th className="text-left py-2.5 px-3 label">Industry</th>
            <Th k="investment_score" label="Inv Score" />
            <Th k="risk_score" label="Risk" />
            <Th k="timing_score" label="Timing" />
            <Th k="best_quarter" label="Best Qtr" />
            <th className="text-left py-2.5 px-3 label">Confidence</th>
            <th className="text-left py-2.5 px-3 label">Entry</th>
            <Th k="enterprise_value" label="EV" />
            <th className="text-left py-2.5 px-3 label">Recommendation</th>
            <th className="text-left py-2.5 px-3 label">Status</th>
            <Th k="priority_score" label="Priority" />
          </tr>
        </thead>
        <tbody>
          {sorted.map((o, i) => (
            <tr key={o.id} className="border-b border-surface-border/50 hover:bg-surface-raised/30">
              <td className="py-2.5 px-3 font-mono text-slate-500">{i + 1}</td>
              <td className="py-2.5 px-3 font-medium text-slate-200">{o.company_name}</td>
              <td className="py-2.5 px-3 text-slate-400">{o.industry}</td>
              <td className="py-2.5 px-3 font-mono" style={{ color: scoreColor(o.investment_score) }}>{o.investment_score}</td>
              <td className="py-2.5 px-3 font-mono" style={{ color: riskColor(o.risk_score) }}>{o.risk_score}</td>
              <td className="py-2.5 px-3 font-mono" style={{ color: timingColor(o.timing_score ?? 0) }}>
                {o.timing_score ?? '—'}
              </td>
              <td className="py-2.5 px-3 text-slate-400">{o.best_quarter ?? '—'}</td>
              <td className="py-2.5 px-3 text-xs text-slate-500">{o.timing_confidence ?? '—'}</td>
              <td className="py-2.5 px-3 text-xs text-slate-500 max-w-[120px] truncate" title={o.entry_assessment ?? ''}>
                {o.entry_assessment ?? '—'}
              </td>
              <td className="py-2.5 px-3 tabular-nums">{fmt.usdM(o.enterprise_value)}</td>
              <td className="py-2.5 px-3 text-xs text-slate-400 max-w-[140px] truncate">{o.recommendation}</td>
              <td className="py-2.5 px-3 text-xs text-slate-500">{o.status}</td>
              <td className="py-2.5 px-3 font-mono text-brand-300">{o.priority_score.toFixed(1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
