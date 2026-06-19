import React from 'react';
import { DealScreenResponse } from '../types';
import { ScoreGauge } from './ScoreGauge';
import { fmt, scoreColor, recommendationStyle } from '../utils';

interface Props { result: DealScreenResponse; }

export const ScoreCard: React.FC<Props> = ({ result: r }) => {
  const dims = [
    { label: 'Growth',          val: r.scores.growth },
    { label: 'Profitability',   val: r.scores.profitability },
    { label: 'Leverage',        val: r.scores.leverage },
    { label: 'Rev. Quality',    val: r.scores.revenue_quality },
    { label: 'Fin. Health',     val: r.scores.financial_health },
  ];

  return (
    <div className="card fade-in-up space-y-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-slate-200">{r.company_name}</h2>
          <p className="text-xs text-slate-500 mt-0.5">{r.industry}</p>
        </div>
        <span
          className="badge border shrink-0"
          style={recommendationStyle(r.recommendation_color)}
        >
          {r.recommendation}
        </span>
      </div>

      <div className="flex justify-around py-2">
        <ScoreGauge score={r.investment_score} label="Investment Score" size={130} />
        <ScoreGauge score={r.risk_score}       label="Risk Score"       size={130} isRisk />
      </div>

      <p className="text-xs text-slate-500 text-center">{r.risk_label}</p>

      {/* Dimension bars */}
      <div className="space-y-2.5">
        {dims.map(d => (
          <div key={d.label} className="flex items-center gap-3">
            <span className="text-xs text-slate-400 w-24 shrink-0">{d.label}</span>
            <div className="flex-1 bg-surface-raised rounded-full h-1.5 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{ width: `${d.val}%`, backgroundColor: scoreColor(d.val) }}
              />
            </div>
            <span className="text-xs font-mono tabular-nums w-7 text-right" style={{ color: scoreColor(d.val) }}>
              {d.val}
            </span>
          </div>
        ))}
      </div>

      {/* Score breakdown */}
      <div className="bg-surface-raised rounded-lg p-3 space-y-2">
        <p className="label">Score Breakdown</p>
        {r.score_breakdown.map(item => (
          <div key={item.dimension} className="flex items-center justify-between text-xs">
            <span className="text-slate-400">{item.dimension} ({item.weight_pct}%)</span>
            <span className="font-mono text-slate-300">{item.formula}</span>
          </div>
        ))}
        <div className="flex items-center justify-between text-xs pt-1 border-t border-surface-border">
          <span className="text-slate-300 font-medium">Investment Score</span>
          <span className="font-mono font-semibold text-brand-300">{r.investment_score}/100</span>
        </div>
      </div>

      {/* EV summary */}
      <div className="bg-surface-raised rounded-lg p-3 grid grid-cols-2 gap-3">
        <div>
          <p className="label mb-1">Enterprise Value</p>
          <p className="text-lg font-semibold tabular-nums text-slate-100">{fmt.usdM(r.enterprise_value)}</p>
          <p className="text-xs text-slate-500 mt-0.5">{r.valuation.method_used}</p>
        </div>
        <div>
          <p className="label mb-1">EV Range (Comps)</p>
          <p className="text-sm font-medium tabular-nums text-slate-300">
            {fmt.usdM(r.comps.ev_range_low)} – {fmt.usdM(r.comps.ev_range_high)}
          </p>
        </div>
      </div>
    </div>
  );
};
