import React from 'react';
import { DealScreenResponse } from '../types';
import { ScoreGauge } from './ScoreGauge';
import { fmt, scoreColor } from '../utils';

interface Props { result: DealScreenResponse; }

const recBg: Record<string, string> = {
  'Strong Buyout Candidate':       'bg-green-500/10  border-green-500/30  text-green-400',
  'Attractive Growth Investment':  'bg-blue-500/10   border-blue-500/30   text-blue-400',
  'Requires Further Due Diligence':'bg-yellow-500/10 border-yellow-500/30 text-yellow-400',
  'High Risk Opportunity':         'bg-orange-500/10 border-orange-500/30 text-orange-400',
  'Reject':                        'bg-red-500/10    border-red-500/30    text-red-400',
};

export const ScoreCard: React.FC<Props> = ({ result: r }) => {
  const recClass = recBg[r.recommendation] ?? recBg['Reject'];
  const dims = [
    { label: 'Growth',          val: r.scores.growth },
    { label: 'Profitability',   val: r.scores.profitability },
    { label: 'Leverage',        val: r.scores.leverage },
    { label: 'Rev. Quality',    val: r.scores.revenue_quality },
    { label: 'Fin. Health',     val: r.scores.financial_health },
  ];

  return (
    <div className="card fade-in-up space-y-5">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-200">{r.company_name}</h2>
          <p className="text-xs text-slate-500 mt-0.5">{r.industry}</p>
        </div>
        <span className={`badge border ${recClass}`}>{r.recommendation}</span>
      </div>

      {/* Gauges */}
      <div className="flex justify-around py-2">
        <ScoreGauge score={r.investment_score} label="Investment Score" size={130} />
        <ScoreGauge score={r.risk_score}       label="Risk Score"       size={130} isRisk />
      </div>

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

      {/* EV summary */}
      <div className="bg-surface-raised rounded-lg p-3 grid grid-cols-2 gap-3">
        <div>
          <p className="label mb-1">Enterprise Value</p>
          <p className="text-lg font-semibold tabular-nums text-slate-100">{fmt.usdM(r.enterprise_value)}</p>
        </div>
        <div>
          <p className="label mb-1">EV Range</p>
          <p className="text-sm font-medium tabular-nums text-slate-300">
            {fmt.usdM(r.comps.ev_range_low)} – {fmt.usdM(r.comps.ev_range_high)}
          </p>
        </div>
      </div>
    </div>
  );
};
