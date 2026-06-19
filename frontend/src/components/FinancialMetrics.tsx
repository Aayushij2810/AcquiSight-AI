import React from 'react';
import { DealScreenResponse } from '../types';
import { fmt } from '../utils';

interface Props { result: DealScreenResponse; input: any; }

export const FinancialMetrics: React.FC<Props> = ({ result: r, input }) => {
  const metrics = [
    { label: 'Revenue',         value: fmt.usdM(input.revenue),          sub: 'LTM' },
    { label: 'EBITDA',          value: fmt.usdM(input.ebitda),           sub: 'LTM' },
    { label: 'EBITDA Margin',   value: fmt.pct(r.ebitda_margin),          sub: 'vs peers' },
    { label: 'Revenue Growth',  value: fmt.pct(input.growth_rate),        sub: 'YoY' },
    { label: 'Net Debt',        value: fmt.usdM(r.net_debt),              sub: 'Debt − Cash' },
    { label: 'Debt / EBITDA',   value: fmt.multiple(r.debt_to_ebitda),    sub: 'Leverage' },
    { label: 'Enterprise Value',value: fmt.usdM(r.enterprise_value),      sub: r.valuation.method_used },
    { label: 'Cash',            value: fmt.usdM(input.cash),              sub: 'On balance sheet' },
  ];

  return (
    <div className="card fade-in-up">
      <h2 className="text-base font-semibold text-slate-200 mb-4">Financial Metrics</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {metrics.map(m => (
          <div key={m.label} className="bg-surface-raised rounded-lg p-3">
            <p className="label mb-1.5">{m.label}</p>
            <p className="text-base font-semibold tabular-nums text-slate-100">{m.value}</p>
            <p className="text-xs text-slate-500 mt-0.5">{m.sub}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
