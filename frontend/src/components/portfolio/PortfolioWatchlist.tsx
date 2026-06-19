import React from 'react';
import { PortfolioHighlight } from '../../types';
import { fmt, scoreColor } from '../../utils';
import { Star } from 'lucide-react';

interface Props {
  opportunities: { id: number; company_name: string; watchlist: boolean }[];
  topScores: PortfolioHighlight[];
  lowestRisk: PortfolioHighlight[];
  fastestGrowth: PortfolioHighlight[];
  onToggleWatchlist: (id: number, watchlist: boolean) => void;
}

const List: React.FC<{ title: string; items: PortfolioHighlight[]; metric: (h: PortfolioHighlight) => string }> = ({
  title, items, metric,
}) => (
  <div className="card">
    <p className="label mb-3">{title}</p>
    {items.length === 0 ? (
      <p className="text-xs text-slate-500">No data yet.</p>
    ) : (
      <ul className="space-y-2">
        {items.map((h, i) => (
          <li key={h.id} className="flex items-center justify-between text-sm">
            <span className="text-slate-300"><span className="text-slate-600 mr-2">{i + 1}.</span>{h.company_name}</span>
            <span className="font-mono text-xs" style={{ color: scoreColor(h.investment_score) }}>{metric(h)}</span>
          </li>
        ))}
      </ul>
    )}
  </div>
);

export const PortfolioWatchlist: React.FC<Props> = ({
  opportunities, topScores, lowestRisk, fastestGrowth, onToggleWatchlist,
}) => {
  const starred = opportunities.filter(o => o.watchlist);

  return (
    <div className="space-y-5">
      <div className="card">
        <p className="label mb-3 flex items-center gap-1"><Star size={12} className="text-yellow-400" /> Watchlist</p>
        {starred.length === 0 ? (
          <p className="text-xs text-slate-500">Star companies when adding to portfolio or toggle below.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {starred.map(o => (
              <span key={o.id} className="badge border border-yellow-500/30 text-yellow-400 bg-yellow-500/10">
                {o.company_name}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <List title="Top 5 — Investment Score" items={topScores} metric={h => `${h.investment_score}/100`} />
        <List title="Top 5 — Lowest Risk" items={lowestRisk} metric={h => `Risk ${h.risk_score}`} />
        <List title="Top 5 — Fastest Growth" items={fastestGrowth} metric={h => fmt.pct(h.growth_rate)} />
      </div>

      <div className="card overflow-x-auto">
        <p className="label mb-3">Toggle Watchlist</p>
        <table className="w-full text-sm">
          <tbody>
            {opportunities.map(o => (
              <tr key={o.id} className="border-b border-surface-border/50">
                <td className="py-2 text-slate-200">{o.company_name}</td>
                <td className="py-2 text-right">
                  <button
                    type="button"
                    onClick={() => onToggleWatchlist(o.id, !o.watchlist)}
                    className={`text-lg ${o.watchlist ? 'text-yellow-400' : 'text-slate-600 hover:text-yellow-400'}`}
                  >
                    ★
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
