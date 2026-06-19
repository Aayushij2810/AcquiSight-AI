import React from 'react';
import { PortfolioOpportunity } from '../../types';
import { fmt, scoreColor, riskColor, recommendationStyle } from '../../utils';
import { CheckCircle, XCircle, Clock } from 'lucide-react';

interface Props {
  opportunities: PortfolioOpportunity[];
  onDecision: (id: number, decision: 'Approved' | 'Rejected' | 'Pending') => void;
}

export const InvestmentCommitteeView: React.FC<Props> = ({ opportunities, onDecision }) => {
  const icDeals = opportunities.filter(
    o => o.status === 'Investment Committee' || o.ic_decision !== 'Pending' || o.investment_score >= 70,
  );

  const DecisionIcon: React.FC<{ d: string }> = ({ d }) => {
    if (d === 'Approved') return <CheckCircle size={14} className="text-green-400" />;
    if (d === 'Rejected') return <XCircle size={14} className="text-red-400" />;
    return <Clock size={14} className="text-yellow-400" />;
  };

  return (
    <div className="space-y-4">
      <div className="card border-brand-500/20 bg-gradient-to-br from-brand-500/5 to-transparent">
        <h3 className="text-base font-semibold text-slate-100">Investment Committee Review</h3>
        <p className="text-xs text-slate-500 mt-1">Premium deal review dashboard — approve or reject pipeline candidates.</p>
      </div>

      {icDeals.length === 0 ? (
        <div className="card text-center py-10 text-slate-500 text-sm">No deals ready for IC review.</div>
      ) : (
        <div className="space-y-3">
          {icDeals.map(o => (
            <div key={o.id} className="card border-surface-border hover:border-brand-500/30 transition-colors">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h4 className="text-lg font-semibold text-slate-100">{o.company_name}</h4>
                  <p className="text-xs text-slate-500">{o.industry} · {o.status}</p>
                  <div className="flex gap-4 mt-2 text-sm font-mono">
                    <span style={{ color: scoreColor(o.investment_score) }}>Investment {o.investment_score}</span>
                    <span style={{ color: riskColor(o.risk_score) }}>Risk {o.risk_score}</span>
                    <span className="text-brand-300">Priority {o.priority_score.toFixed(1)}</span>
                  </div>
                  <p className="text-sm text-slate-400 mt-2">{fmt.usdM(o.enterprise_value)} EV</p>
                  <span className="badge border mt-2" style={recommendationStyle('#3b82f6')}>{o.recommendation}</span>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <div className="flex items-center gap-2 text-sm">
                    <DecisionIcon d={o.ic_decision} />
                    <span className="text-slate-300">{o.ic_decision}</span>
                  </div>
                  <div className="flex gap-2">
                    <button type="button" className="btn-ghost text-green-400 border-green-500/30 text-xs" onClick={() => onDecision(o.id, 'Approved')}>
                      Approve
                    </button>
                    <button type="button" className="btn-ghost text-red-400 border-red-500/30 text-xs" onClick={() => onDecision(o.id, 'Rejected')}>
                      Reject
                    </button>
                  </div>
                </div>
              </div>
              {o.memo?.sections && (
                <div className="mt-4 pt-4 border-t border-surface-border">
                  <p className="label mb-2">Investment Memo</p>
                  <p className="text-xs text-slate-400 line-clamp-3">
                    {o.memo.sections[0]?.content || 'No memo generated.'}
                  </p>
                </div>
              )}
              {o.notes && (
                <p className="text-xs text-slate-500 mt-2 border-t border-surface-border pt-2">
                  <span className="font-medium">IC Notes:</span> {o.notes}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
