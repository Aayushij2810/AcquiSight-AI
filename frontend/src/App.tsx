import React, { useState, useCallback } from 'react';
import { Logo } from './components/Logo';
import { ScreeningForm } from './components/ScreeningForm';
import { ScoreCard } from './components/ScoreCard';
import { FinancialMetrics } from './components/FinancialMetrics';
import { CompsTable } from './components/CompsTable';
import { RiskPanel } from './components/RiskPanel';
import { MemoPanel } from './components/MemoPanel';
import { ScoreRadar, ScoreBar } from './components/ScoreChart';
import { screenDeal, generateMemo } from './api';
import { DealScreenResponse, MemoSection, ScreeningFormData } from './types';
import { AlertCircle, Github, TrendingUp } from 'lucide-react';

export default function App() {
  const [result,       setResult]       = useState<DealScreenResponse | null>(null);
  const [inputData,    setInputData]    = useState<any>(null);
  const [screening,    setScreening]    = useState(false);
  const [memoLoading,  setMemoLoading]  = useState(false);
  const [memoSections, setMemoSections] = useState<MemoSection[]>([]);
  const [memoDate,     setMemoDate]     = useState('');
  const [error,        setError]        = useState<string | null>(null);

  const handleScreen = useCallback(async (form: ScreeningFormData) => {
    setScreening(true);
    setError(null);
    setResult(null);
    setMemoSections([]);
    try {
      const payload = {
        company_name: form.company_name,
        industry:     form.industry,
        revenue:      parseFloat(form.revenue),
        ebitda:       parseFloat(form.ebitda),
        growth_rate:  parseFloat(form.growth_rate),
        debt:         parseFloat(form.debt),
        cash:         parseFloat(form.cash),
        country:      form.country,
      };
      const data = await screenDeal(payload);
      setResult(data);
      setInputData(payload);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message || 'Screening failed. Is the backend running?');
    } finally {
      setScreening(false);
    }
  }, []);

  const handleGenerateMemo = useCallback(async () => {
    if (!result) return;
    setMemoLoading(true);
    try {
      const memo = await generateMemo(result);
      setMemoSections(memo.sections);
      setMemoDate(memo.generated_at);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Memo generation failed.');
    } finally {
      setMemoLoading(false);
    }
  }, [result]);

  return (
    <div className="min-h-screen bg-surface text-slate-200">
      {/* Header */}
      <header className="border-b border-surface-border sticky top-0 z-30 bg-surface/90 backdrop-blur-sm">
        <div className="max-w-screen-xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Logo size={28} />
            <div>
              <span className="font-semibold text-slate-100 text-sm">AcquiSight AI</span>
              <span className="hidden sm:inline text-slate-500 text-xs ml-2">Deal Screening & Investment Intelligence</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <a
              href="https://github.com/Aayushij2810/AcquiSight-AI"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-ghost"
            >
              <Github size={14} /> GitHub
            </a>
          </div>
        </div>
      </header>

      {/* Hero strip */}
      <div className="border-b border-surface-border bg-surface-card">
        <div className="max-w-screen-xl mx-auto px-4 sm:px-6 py-4 flex items-center gap-3">
          <TrendingUp size={18} className="text-brand-400" />
          <p className="text-sm text-slate-400">
            <span className="text-slate-200 font-medium">AI-Powered PE Deal Screening.</span>{' '}
            Enter company financials below to generate an instant investment attractiveness score, risk assessment, and comparable company analysis.
          </p>
        </div>
      </div>

      <main className="max-w-screen-xl mx-auto px-4 sm:px-6 py-6 space-y-6">

        {/* Error banner */}
        {error && (
          <div className="flex items-start gap-3 bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400 fade-in-up">
            <AlertCircle size={18} className="shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-sm">Error</p>
              <p className="text-xs mt-0.5 opacity-80">{error}</p>
            </div>
          </div>
        )}

        {/* Input form */}
        <ScreeningForm onSubmit={handleScreen} loading={screening} />

        {/* Loading skeleton */}
        {screening && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="card space-y-3">
                <div className="skeleton h-5 w-40" />
                <div className="skeleton h-24" />
                <div className="skeleton h-4 w-3/4" />
                <div className="skeleton h-4 w-1/2" />
              </div>
            ))}
          </div>
        )}

        {/* Results */}
        {result && !screening && (
          <>
            {/* Row 1: Score + Metrics */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              <ScoreCard result={result} />
              <div className="lg:col-span-2">
                <FinancialMetrics result={result} input={inputData} />
              </div>
            </div>

            {/* Row 2: Charts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <ScoreRadar scores={result.scores} />
              <ScoreBar   scores={result.scores} />
            </div>

            {/* Row 3: Risk + Comps */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <RiskPanel  result={result} />
              <CompsTable comps={result.comps} />
            </div>

            {/* Row 4: Memo */}
            <MemoPanel
              sections={memoSections}
              companyName={result.company_name}
              generatedAt={memoDate}
              loading={memoLoading}
              onGenerate={handleGenerateMemo}
            />
          </>
        )}

        {/* Empty state */}
        {!result && !screening && !error && (
          <div className="card text-center py-16 fade-in-up">
            <Logo size={48} />
            <h3 className="mt-4 text-lg font-semibold text-slate-200">Ready to Screen a Deal</h3>
            <p className="text-sm text-slate-500 mt-2 max-w-sm mx-auto">
              Fill in the company details above and click "Screen Company" to generate a full
              investment attractiveness analysis.
            </p>
          </div>
        )}
      </main>

      <footer className="border-t border-surface-border mt-12">
        <div className="max-w-screen-xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <p className="text-xs text-slate-600">AcquiSight AI — For informational purposes only. Not investment advice.</p>
          <p className="text-xs text-slate-600">Built with React · FastAPI · OpenAI</p>
        </div>
      </footer>
    </div>
  );
}
