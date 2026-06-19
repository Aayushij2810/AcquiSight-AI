import React from 'react';
import { PortfolioOpportunity, PIPELINE_STAGES } from '../../types';
import { fmt, scoreColor, riskColor, recommendationStyle } from '../../utils';

interface Props {
  opportunities: PortfolioOpportunity[];
  onStatusChange: (id: number, status: string) => void;
}

export const PipelineKanban: React.FC<Props> = ({ opportunities, onStatusChange }) => {
  const onDragStart = (e: React.DragEvent, id: number) => {
    e.dataTransfer.setData('oppId', String(id));
  };

  const onDrop = (e: React.DragEvent, stage: string) => {
    e.preventDefault();
    const id = Number(e.dataTransfer.getData('oppId'));
    if (id) onStatusChange(id, stage);
  };

  const onDragOver = (e: React.DragEvent) => e.preventDefault();

  return (
    <div className="flex gap-3 overflow-x-auto pb-2">
      {PIPELINE_STAGES.map(stage => {
        const cards = opportunities.filter(o => o.status === stage);
        return (
          <div
            key={stage}
            className="min-w-[240px] flex-1 bg-surface-raised/40 border border-surface-border rounded-xl p-3"
            onDrop={e => onDrop(e, stage)}
            onDragOver={onDragOver}
          >
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs font-semibold text-slate-300 uppercase tracking-wide">{stage}</p>
              <span className="text-xs text-slate-500 bg-surface-card px-2 py-0.5 rounded-full">{cards.length}</span>
            </div>
            <div className="space-y-2 min-h-[120px]">
              {cards.map(o => (
                <div
                  key={o.id}
                  draggable
                  onDragStart={e => onDragStart(e, o.id)}
                  className="bg-surface-card border border-surface-border rounded-lg p-3 cursor-grab active:cursor-grabbing hover:border-brand-500/40 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-medium text-slate-200 truncate">{o.company_name}</p>
                    {o.watchlist && <span className="text-yellow-400 text-xs">★</span>}
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">{o.industry}</p>
                  <div className="flex gap-2 mt-2 text-xs font-mono">
                    <span style={{ color: scoreColor(o.investment_score) }}>Inv {o.investment_score}</span>
                    <span style={{ color: riskColor(o.risk_score) }}>Risk {o.risk_score}</span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1 tabular-nums">{fmt.usdM(o.enterprise_value)}</p>
                  <span
                    className="badge border mt-2 text-[10px]"
                    style={recommendationStyle('#64748b')}
                  >
                    {o.recommendation}
                  </span>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};
