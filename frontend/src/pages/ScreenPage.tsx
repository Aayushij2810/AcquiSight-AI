import React, { useState, useCallback } from 'react';
import { ScreeningForm } from '../components/ScreeningForm';
import { ScoreCard } from '../components/ScoreCard';
import { FinancialMetrics } from '../components/FinancialMetrics';
import { CompsTable } from '../components/CompsTable';
import { RiskPanel } from '../components/RiskPanel';
import { MemoPanel } from '../components/MemoPanel';
import { ValuationMethodologyPanel } from '../components/ValuationMethodologyPanel';
import { ScoreRadar, ScoreBar } from '../components/ScoreChart';
import { AddToPortfolioButton } from '../components/portfolio/AddToPortfolioButton';
import { screenDeal, generateMemo } from '../api';
import { DealScreenResponse, MemoSection, MemoResponse, ScreeningFormData } from '../types';
import { AlertCircle, TrendingUp } from 'lucide-react';

export const ScreenPage: React.FC = () => {
  const [result, setResult] = useState<DealScreenResponse | null>(null);
  const [inputData, setInputData] = useState<{
    revenue: number; ebitda: number; growth_rate: number; debt: number; cash: number;
  } | null>(null);
  const [screening, setScreening] = useState(false);
  const [memoLoading, setMemoLoading] = useState(false);
  const [memoSections, setMemoSections] = useState<MemoSection[]>([]);
  const [memoDate, setMemoDate] = useState('');
  const [memo, setMemo] = useState<MemoResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScreen = useCallback(async (form: ScreeningFormData) => {
    setScreening(true);
    setError(null);
    setResult(null);
    setMemoSections([]);
    setMemo(null);
    try {
      const payload: Record<string, string | number> = {
        company_name: form.company_name,
        industry: form.industry,
        revenue: parseFloat(form.revenue),
        ebitda: parseFloat(form.ebitda),
        growth_rate: parseFloat(form.growth_rate),
        debt: parseFloat(form.debt),
        cash: parseFloat(form.cash),
        country: form.country,
      };
      if (form.market_cap.trim()) payload.market_cap = parseFloat(form.market_cap);
      const data = await screenDeal(payload);
      setResult(data);
      setInputData({
        revenue: payload.revenue as number,
        ebitda: payload.ebitda as number,
        growth_rate: payload.growth_rate as number,
        debt: payload.debt as number,
        cash: payload.cash as number,
      });
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message || 'Screening failed.');
    } finally {
      setScreening(false);
    }
  }, []);

  const handleGenerateMemo = useCallback(async () => {
    if (!result) return;
    setMemoLoading(true);
    try {
      const m = await generateMemo(result);
      setMemoSections(m.sections);
      setMemoDate(m.generated_at);
      setMemo(m);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Memo generation failed.');
    } finally {
      setMemoLoading(false);
    }
  }, [result]);

  return (
    <div className="space-y-6">
      <div className="border border-surface-border bg-surface-card rounded-xl px-4 py-3 flex items-center gap-3">
        <TrendingUp size={18} className="text-brand-400 shrink-0" />
        <p className="text-sm text-slate-400">
          <span className="text-slate-200 font-medium">Screen Company.</span>{' '}
          Evaluate a target and add it to your deal pipeline.
        </p>
      </div>

      {error && (
        <div className="flex items-start gap-3 bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400">
          <AlertCircle size={18} className="shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-sm">Error</p>
            <p className="text-xs mt-0.5 opacity-80">{error}</p>
          </div>
        </div>
      )}

      <ScreeningForm onSubmit={handleScreen} loading={screening} />

      {screening && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="card space-y-3">
              <div className="skeleton h-5 w-40" />
              <div className="skeleton h-24" />
            </div>
          ))}
        </div>
      )}

      {result && inputData && !screening && (
        <>
          <AddToPortfolioButton result={result} input={inputData} memo={memo} />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            <ScoreCard result={result} />
            <div className="lg:col-span-2"><FinancialMetrics result={result} input={inputData} /></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <ScoreRadar scores={result.scores} />
            <ScoreBar scores={result.scores} />
          </div>
          <ValuationMethodologyPanel result={result} />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <RiskPanel result={result} />
            <CompsTable comps={result.comps} />
          </div>
          <MemoPanel
            sections={memoSections}
            companyName={result.company_name}
            generatedAt={memoDate}
            loading={memoLoading}
            onGenerate={handleGenerateMemo}
          />
        </>
      )}
    </div>
  );
};
