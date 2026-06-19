import React from 'react';
import { CompsResult } from '../types';
import { fmt } from '../utils';

interface Props { comps: CompsResult; }

export const CompsTable: React.FC<Props> = ({ comps }) => (
  <div className="card fade-in-up">
    <div className="flex items-center justify-between mb-4">
      <h2 className="text-base font-semibold text-slate-200">Comparable Companies</h2>
      <span className="text-xs text-slate-500">
        Low {comps.bear_multiple.toFixed(1)}x · Avg {comps.base_multiple.toFixed(1)}x · High {comps.bull_multiple.toFixed(1)}x
      </span>
    </div>
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-surface-border">
            {['Company', 'EV/EBITDA', 'EBITDA Margin', 'Revenue Growth'].map(h => (
              <th key={h} className="text-left py-2.5 px-3 label first:pl-0">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {comps.companies.map(c => (
            <tr
              key={c.name}
              className="border-b border-surface-border/50 hover:bg-surface-raised/50 transition-colors"
            >
              <td className="py-2.5 px-3 first:pl-0 font-medium text-slate-200">{c.name}</td>
              <td className="py-2.5 px-3 tabular-nums font-mono text-brand-400">{c.ev_ebitda_multiple.toFixed(1)}x</td>
              <td className="py-2.5 px-3 tabular-nums">
                {c.ebitda_margin != null ? fmt.pct(c.ebitda_margin) : '—'}
              </td>
              <td className="py-2.5 px-3 tabular-nums">
                {c.revenue_growth != null ? (
                  <span className={c.revenue_growth >= 0 ? 'text-green-400' : 'text-red-400'}>
                    {c.revenue_growth >= 0 ? '+' : ''}{fmt.pct(c.revenue_growth)}
                  </span>
                ) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="border-t-2 border-surface-border">
            <td className="pt-3 pl-0 font-semibold text-slate-300">Peer Average</td>
            <td className="pt-3 px-3 tabular-nums font-mono font-semibold text-brand-300">
              {comps.base_multiple.toFixed(1)}x
            </td>
            <td className="pt-3 px-3 tabular-nums text-slate-400">—</td>
            <td className="pt-3 px-3 tabular-nums text-slate-400">—</td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div className="mt-4 space-y-2">
      <p className="label">Comparable Valuation Scenarios</p>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {comps.cases.map(item => (
          <div key={item.label} className="bg-surface-raised rounded-lg p-3">
            <p className="label mb-1">{item.label}</p>
            <p className="text-sm font-semibold tabular-nums text-slate-100">{fmt.usdM(item.enterprise_value)}</p>
            <p className="text-xs font-mono text-slate-500 mt-1.5">{item.calculation}</p>
          </div>
        ))}
      </div>
    </div>
  </div>
);
