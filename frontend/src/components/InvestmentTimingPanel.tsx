import React from 'react';
import { Clock, TrendingUp, AlertTriangle, Shield, Info } from 'lucide-react';
import { TimingAnalysis } from '../types';
import { ScoreGauge } from './ScoreGauge';
import { timingColor } from '../utils';

interface Props { timing: TimingAnalysis }

export const InvestmentTimingPanel: React.FC<Props> = ({ timing: t }) => {
  const color = timingColor(t.timing_score);

  return (
    <div className="card fade-in-up border-brand-500/20 space-y-5">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 className="text-base font-semibold text-slate-200 flex items-center gap-2">
            <Clock size={18} className="text-brand-400" />
            Investment Timing Intelligence
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Analytical assessment based on fundamentals, valuation, and sector trends — not financial advice.
          </p>
        </div>
        <div className="text-right">
          <p className="label">Confidence</p>
          <p className="text-sm font-semibold text-slate-200">{t.confidence_level}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="flex flex-col items-center justify-center bg-surface-raised rounded-xl p-4">
          <ScoreGauge score={t.timing_score} label="Investment Timing Score" size={140} getColor={timingColor} />
          <p className="text-sm font-semibold mt-2" style={{ color }}>{t.status}</p>
          <p className="text-xs text-slate-500 mt-1">{t.entry_window_assessment}</p>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div className="bg-surface-raised rounded-xl p-4">
            <p className="label mb-3">Quarter Attractiveness Analysis</p>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-border">
                  <th className="text-left py-2 label">Quarter</th>
                  <th className="text-left py-2 label">Score</th>
                  <th className="text-left py-2 label">Outlook</th>
                </tr>
              </thead>
              <tbody>
                {t.quarter_analysis.map(q => (
                  <tr
                    key={q.quarter}
                    className={`border-b border-surface-border/50 ${
                      q.quarter === t.best_quarter ? 'bg-brand-500/10' : ''
                    }`}
                  >
                    <td className="py-2 text-slate-200 font-medium">
                      {q.quarter}
                      {q.quarter === t.best_quarter && (
                        <span className="ml-2 text-[10px] text-brand-400 uppercase">Most Attractive</span>
                      )}
                    </td>
                    <td className="py-2 font-mono" style={{ color: timingColor(q.attractiveness_score) }}>
                      {q.attractiveness_score}
                    </td>
                    <td className="py-2 text-slate-400">{q.outlook}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="bg-surface-raised rounded-xl p-4">
            <p className="label mb-2 flex items-center gap-1">
              <TrendingUp size={12} /> Entry Window Assessment
            </p>
            <p className="text-sm font-medium text-slate-200 mb-2">{t.entry_window_assessment}</p>
            <ul className="space-y-1">
              {t.entry_window_reasons.map((r, i) => (
                <li key={i} className="text-xs text-slate-400 flex gap-2">
                  <span className="text-brand-400">•</span> {r}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-surface-raised rounded-xl p-4">
          <p className="label mb-3 flex items-center gap-1 text-green-400">
            <TrendingUp size={12} /> Positive Catalysts
          </p>
          <div className="space-y-2">
            {t.positive_catalysts.map((c, i) => (
              <div key={i} className="text-xs">
                <p className="text-slate-200 font-medium">{c.name}</p>
                <p className="text-slate-500 mt-0.5">{c.description}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-surface-raised rounded-xl p-4">
          <p className="label mb-3 flex items-center gap-1 text-orange-400">
            <AlertTriangle size={12} /> Potential Headwinds
          </p>
          <div className="space-y-2">
            {t.risk_catalysts.map((c, i) => (
              <div key={i} className="text-xs">
                <p className="text-slate-200 font-medium">{c.name}</p>
                <p className="text-slate-500 mt-0.5">{c.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-surface-raised rounded-xl p-4">
        <p className="label mb-2">Industry Timing Factors Considered</p>
        <div className="flex flex-wrap gap-2">
          {t.industry_timing_factors.map((f, i) => (
            <span key={i} className="badge border border-surface-border text-slate-400 text-[10px]">{f}</span>
          ))}
        </div>
      </div>

      <div className="bg-brand-500/5 border border-brand-500/20 rounded-xl p-4">
        <p className="label mb-2 flex items-center gap-1">
          <Shield size={12} /> Analyst Commentary
        </p>
        <p className="text-sm text-slate-300 leading-relaxed">{t.analyst_commentary}</p>
      </div>

      <div className="flex items-start gap-2 text-xs text-slate-600">
        <Info size={14} className="shrink-0 mt-0.5" />
        <p>{t.disclaimer}</p>
      </div>
    </div>
  );
};
