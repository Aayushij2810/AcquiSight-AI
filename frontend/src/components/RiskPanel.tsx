import React from 'react';
import { AlertTriangle, XCircle, AlertCircle, Info } from 'lucide-react';
import { DealScreenResponse } from '../types';
import { riskColor, severityColor } from '../utils';

const SeverityIcon: React.FC<{ s: string }> = ({ s }) => {
  if (s === 'Critical') return <XCircle size={14} className="text-red-400" />;
  if (s === 'High')     return <AlertTriangle size={14} className="text-orange-400" />;
  if (s === 'Medium')   return <AlertCircle size={14} className="text-yellow-400" />;
  return <Info size={14} className="text-green-400" />;
};

interface Props { result: DealScreenResponse; }

export const RiskPanel: React.FC<Props> = ({ result: r }) => {
  const color = riskColor(r.risk_score);

  return (
    <div className="card fade-in-up space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-200">Risk Analysis</h2>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
          <span className="text-sm font-medium" style={{ color }}>{r.risk_label}</span>
        </div>
      </div>

      <div className="bg-surface-raised rounded-full h-2 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${r.risk_score}%`, backgroundColor: color }}
        />
      </div>

      <div className="bg-surface-raised rounded-lg p-3 space-y-2">
        <p className="label">Risk Score Breakdown</p>
        {r.risk_breakdown.map(item => (
          <div key={item.dimension} className="flex items-center justify-between text-xs">
            <span className="text-slate-400">{item.dimension} ({item.weight_pct}%)</span>
            <span className="font-mono text-slate-300">
              {item.sub_score} × {item.weight_pct}% = {item.weighted_contribution}
            </span>
          </div>
        ))}
        <div className="flex items-center justify-between text-xs pt-1 border-t border-surface-border">
          <span className="text-slate-300 font-medium">Composite Risk Score</span>
          <span className="font-mono font-semibold" style={{ color }}>{r.risk_score}/100</span>
        </div>
      </div>

      <div className="space-y-3">
        <p className="label">Risk Drivers</p>
        {r.risk_factors.map((f, i) => (
          <div key={i} className={`rounded-lg p-3 border ${severityColor(f.severity)}`}>
            <div className="flex items-center gap-2 mb-1">
              <SeverityIcon s={f.severity} />
              <span className="text-xs font-semibold">{f.name}</span>
              <span className="text-xs text-slate-500 ml-1">({f.category})</span>
              <span className={`badge border ml-auto ${severityColor(f.severity)}`}>{f.severity}</span>
            </div>
            <p className="text-xs opacity-80 mb-1.5">{f.description}</p>
            <p className="text-xs opacity-60"><span className="font-medium">Mitigation: </span>{f.mitigation}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
