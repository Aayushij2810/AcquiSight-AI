import React from 'react';
import { AlertTriangle, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { DealScreenResponse } from '../types';
import { riskColor, severityColor } from '../utils';

const riskFactors = (r: DealScreenResponse) => {
  const factors: { category: string; name: string; severity: string; description: string; mitigation: string; }[] = [];
  if (r.debt_to_ebitda && r.debt_to_ebitda > 6)
    factors.push({ category: 'Leverage', name: 'Excessive Leverage', severity: 'Critical',
      description: `Debt/EBITDA of ${r.debt_to_ebitda.toFixed(1)}x far exceeds the 5x PE threshold.`,
      mitigation: 'Immediate deleveraging plan; refinancing or asset disposals within 24 months.' });
  else if (r.debt_to_ebitda && r.debt_to_ebitda > 4)
    factors.push({ category: 'Leverage', name: 'High Leverage', severity: 'High',
      description: `Debt/EBITDA of ${r.debt_to_ebitda.toFixed(1)}x constrains post-acquisition flexibility.`,
      mitigation: 'Model accelerated repayment from operating cashflows over 3–5 years.' });
  if (r.ebitda_margin < 5)
    factors.push({ category: 'Operational', name: 'Thin Margins', severity: 'High',
      description: `EBITDA margin of ${r.ebitda_margin.toFixed(1)}% leaves minimal operational buffer.`,
      mitigation: 'SG&A rationalisation and pricing power review within 12 months of close.' });
  if (r.scores.growth < 30)
    factors.push({ category: 'Market', name: 'Slow Growth', severity: 'Medium',
      description: 'Revenue growth below market average indicates competitive or cyclical pressure.',
      mitigation: 'Evaluate adjacency expansion and bolt-on M&A as post-acquisition levers.' });
  return factors;
};

const SeverityIcon: React.FC<{ s: string }> = ({ s }) => {
  if (s === 'Critical') return <XCircle     size={14} className="text-red-400" />;
  if (s === 'High')     return <AlertTriangle size={14} className="text-orange-400" />;
  if (s === 'Medium')   return <AlertCircle  size={14} className="text-yellow-400" />;
  return                       <CheckCircle  size={14} className="text-green-400" />;
};

interface Props { result: DealScreenResponse; }

export const RiskPanel: React.FC<Props> = ({ result: r }) => {
  const factors = riskFactors(r);
  const color   = riskColor(r.risk_score);
  const label   = r.risk_score <= 25 ? 'Low' : r.risk_score <= 50 ? 'Medium' : r.risk_score <= 70 ? 'High' : 'Very High';

  return (
    <div className="card fade-in-up space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-200">Risk Analysis</h2>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
          <span className="text-sm font-medium" style={{ color }}>{label} Risk</span>
        </div>
      </div>

      {/* Risk score bar */}
      <div className="bg-surface-raised rounded-full h-2 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${r.risk_score}%`, backgroundColor: color }}
        />
      </div>

      {/* Risk factors */}
      {factors.length === 0 ? (
        <div className="flex items-center gap-2 text-green-400 text-sm">
          <CheckCircle size={16} /> No material risk factors identified at this stage.
        </div>
      ) : (
        <div className="space-y-3">
          {factors.map((f, i) => (
            <div key={i} className={`rounded-lg p-3 border ${severityColor(f.severity)}`}>
              <div className="flex items-center gap-2 mb-1">
                <SeverityIcon s={f.severity} />
                <span className="text-xs font-semibold">{f.name}</span>
                <span className={`badge border ml-auto ${severityColor(f.severity)}`}>{f.severity}</span>
              </div>
              <p className="text-xs opacity-80 mb-1.5">{f.description}</p>
              <p className="text-xs opacity-60"><span className="font-medium">Mitigation: </span>{f.mitigation}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
