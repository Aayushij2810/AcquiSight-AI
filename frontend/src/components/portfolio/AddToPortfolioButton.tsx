import React, { useState } from 'react';
import { Briefcase, Star, CheckCircle2 } from 'lucide-react';
import { addToPortfolio } from '../../api';
import { DealScreenResponse, MemoResponse } from '../../types';

interface Props {
  result: DealScreenResponse;
  input: {
    revenue: number;
    ebitda: number;
    growth_rate: number;
    debt: number;
    cash: number;
  };
  memo?: MemoResponse | null;
  onAdded?: () => void;
}

export const AddToPortfolioButton: React.FC<Props> = ({ result, input, memo, onAdded }) => {
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [watchlist, setWatchlist] = useState(false);

  const handleAdd = async () => {
    setLoading(true);
    setError(null);
    try {
      await addToPortfolio({
        screen_result: result,
        revenue: input.revenue,
        ebitda: input.ebitda,
        growth_rate: input.growth_rate,
        debt: input.debt,
        cash: input.cash,
        watchlist,
        memo: memo || undefined,
      });
      setDone(true);
      onAdded?.();
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to add to portfolio.');
    } finally {
      setLoading(false);
    }
  };

  if (done) {
    return (
      <div className="flex items-center gap-2 text-green-400 text-sm bg-green-500/10 border border-green-500/30 rounded-lg px-4 py-3">
        <CheckCircle2 size={16} />
        <span>{result.company_name} added to portfolio.</span>
      </div>
    );
  }

  return (
    <div className="card border-brand-500/20 bg-brand-500/5 space-y-3">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <p className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Briefcase size={16} className="text-brand-400" />
            Save to Deal Pipeline
          </p>
          <p className="text-xs text-slate-500 mt-0.5">
            Track, compare, and prioritise {result.company_name} in Portfolio Mode.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-1.5 text-xs text-slate-400 cursor-pointer">
            <input
              type="checkbox"
              checked={watchlist}
              onChange={e => setWatchlist(e.target.checked)}
              className="rounded border-surface-border"
            />
            <Star size={12} /> Watchlist
          </label>
          <button type="button" className="btn-primary" onClick={handleAdd} disabled={loading}>
            {loading ? 'Adding…' : 'Add to Portfolio'}
          </button>
        </div>
      </div>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
};
