import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Database, Search, AlertTriangle, CheckCircle2, Loader2 } from 'lucide-react';
import { lookupCompany, searchCompanies } from '../api';
import { CompanyIntelligence, CompanySearchMatch, ScreeningFormData } from '../types';
import { fmt } from '../utils';

interface Props {
  onApply: (data: ScreeningFormData, intel: CompanyIntelligence) => void;
}

function parseLookupError(e: unknown): { message: string; suggestions: CompanySearchMatch[] } {
  const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
  if (detail && typeof detail === 'object' && detail !== null && 'message' in detail) {
    const d = detail as { message: string; suggestions?: CompanySearchMatch[] };
    return { message: d.message, suggestions: d.suggestions || [] };
  }
  if (typeof detail === 'string') return { message: detail, suggestions: [] };
  return { message: 'Company lookup failed.', suggestions: [] };
}

export const CompanyLookup: React.FC<Props> = ({ onApply }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<CompanySearchMatch[]>([]);
  const [autocomplete, setAutocomplete] = useState<CompanySearchMatch[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [intel, setIntel] = useState<CompanyIntelligence | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  const runLookup = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError(null);
    setSuggestions([]);
    setIntel(null);
    setShowDropdown(false);
    try {
      const data = await lookupCompany(searchQuery.trim());
      setIntel(data);
    } catch (e: unknown) {
      const parsed = parseLookupError(e);
      setError(parsed.message);
      setSuggestions(parsed.suggestions);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleLookup = () => runLookup(query);

  const selectSuggestion = (match: CompanySearchMatch) => {
    const label = `${match.company_name} (${match.ticker})`;
    setQuery(label);
    setShowDropdown(false);
    runLookup(match.ticker);
  };

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    const q = query.trim();
    if (q.length < 2) {
      setAutocomplete([]);
      return;
    }
    debounceRef.current = setTimeout(async () => {
      try {
        const res = await searchCompanies(q, 8);
        setAutocomplete(res.results);
        setShowDropdown(res.results.length > 0);
      } catch {
        setAutocomplete([]);
      }
    }, 280);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query]);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  const applyToForm = () => {
    if (!intel) return;
    onApply({
      company_name: intel.company_name,
      industry: intel.industry,
      revenue: String(Math.round(intel.revenue)),
      ebitda: String(Math.round(intel.ebitda)),
      growth_rate: String(intel.revenue_growth.toFixed(1)),
      debt: String(Math.round(intel.debt)),
      cash: String(Math.round(intel.cash)),
      country: intel.country,
      market_cap: intel.market_cap ? String(Math.round(intel.market_cap)) : '',
    }, intel);
  };

  return (
    <div className="card border-brand-500/25 bg-brand-500/5 space-y-4 mb-6">
      <div>
        <h2 className="text-base font-semibold text-slate-200 flex items-center gap-2">
          <Database size={18} className="text-brand-400" />
          Company Intelligence Engine
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Type any public company — Google, Facebook, Nvidia, Adobe, JPMorgan. Intelligent resolution finds the correct ticker.
        </p>
      </div>

      <div className="flex gap-2 relative" ref={wrapperRef}>
        <div className="flex-1 relative">
          <input
            className="input w-full"
            placeholder="Microsoft, Meta, Adobe, GOOGL…"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onFocus={() => autocomplete.length > 0 && setShowDropdown(true)}
            onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), handleLookup())}
            autoComplete="off"
          />
          {showDropdown && autocomplete.length > 0 && (
            <ul className="absolute z-20 top-full left-0 right-0 mt-1 bg-surface-raised border border-slate-700 rounded-lg shadow-xl max-h-56 overflow-y-auto">
              {autocomplete.map(m => (
                <li key={m.ticker}>
                  <button
                    type="button"
                    className="w-full text-left px-3 py-2 text-sm hover:bg-brand-500/10 flex justify-between gap-2"
                    onClick={() => selectSuggestion(m)}
                  >
                    <span className="text-slate-200 truncate">{m.company_name}</span>
                    <span className="text-brand-400 shrink-0 font-mono text-xs">{m.ticker}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
        <button type="button" className="btn-primary shrink-0" onClick={handleLookup} disabled={loading}>
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
          Lookup
        </button>
      </div>

      {error && (
        <div className="space-y-2">
          <p className="text-xs text-red-400">{error}</p>
          {suggestions.length > 0 && (
            <div className="bg-surface-raised rounded-lg p-3 space-y-2">
              <p className="text-xs text-slate-400">Did you mean:</p>
              <div className="flex flex-wrap gap-2">
                {suggestions.map(s => (
                  <button
                    key={s.ticker}
                    type="button"
                    className="text-xs px-2 py-1 rounded-md bg-brand-500/15 text-brand-300 hover:bg-brand-500/25"
                    onClick={() => selectSuggestion(s)}
                  >
                    {s.company_name} ({s.ticker})
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {intel && (
        <div className="space-y-4 fade-in-up">
          {intel.resolution && (
            <p className="text-[10px] text-slate-500">
              Resolved via {intel.resolution.source.replace(/_/g, ' ')} · {intel.resolution.match_type.replace(/_/g, ' ')} · {intel.resolution.resolved_ticker}
            </p>
          )}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <ProvenanceCard label="Data Source" value={intel.provenance.data_source} />
            <ProvenanceCard label="Reliability" value={`${intel.provenance.reliability_score}/100`} sub={intel.provenance.reliability_grade} />
            <ProvenanceCard label="Confidence" value={intel.provenance.confidence} />
            <ProvenanceCard
              label="Last Updated"
              value={new Date(intel.provenance.last_updated).toLocaleString()}
              sub={intel.provenance.fiscal_period ? `FY ${intel.provenance.fiscal_period}` : intel.provenance.data_freshness}
            />
          </div>

          {intel.cross_validation?.flagged && (
            <div className="flex items-start gap-2 bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 text-yellow-400 text-xs">
              <AlertTriangle size={14} className="shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">{intel.cross_validation.message}</p>
                {intel.cross_validation.discrepancies.map(d => (
                  <p key={d.field} className="mt-1 opacity-80">
                    {d.field}: {Object.entries(d.values).map(([k, v]) => `${k} ${fmt.usdM(v)}`).join(' vs ')}
                    {' '}({d.max_difference_pct}% variance)
                  </p>
                ))}
              </div>
            </div>
          )}

          {intel.cross_validation && !intel.cross_validation.flagged && (
            <div className="flex items-center gap-2 text-green-400 text-xs">
              <CheckCircle2 size={14} /> {intel.cross_validation.message}
            </div>
          )}

          <div className="bg-surface-raised rounded-lg p-3 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
            <Stat label="Ticker" value={intel.ticker} />
            <Stat label="Revenue" value={fmt.usdM(intel.revenue)} />
            <Stat label="EBITDA" value={fmt.usdM(intel.ebitda)} />
            <Stat label="Growth" value={fmt.pct(intel.revenue_growth)} />
            <Stat label="EV" value={intel.enterprise_value ? fmt.usdM(intel.enterprise_value) : '—'} />
            <Stat label="Market Cap" value={intel.market_cap ? fmt.usdM(intel.market_cap) : '—'} />
            <Stat label="Industry" value={intel.industry} />
            <Stat label="Country" value={intel.country} />
          </div>

          <button type="button" className="btn-primary w-full justify-center" onClick={applyToForm}>
            Apply to Screening Form
          </button>
        </div>
      )}
    </div>
  );
};

const ProvenanceCard: React.FC<{ label: string; value: string; sub?: string }> = ({ label, value, sub }) => (
  <div className="bg-surface-raised rounded-lg p-3">
    <p className="label mb-1">{label}</p>
    <p className="text-sm font-medium text-slate-200 truncate" title={value}>{value}</p>
    {sub && <p className="text-[10px] text-slate-500 mt-0.5">{sub}</p>}
  </div>
);

const Stat: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div>
    <p className="text-slate-500">{label}</p>
    <p className="text-slate-200 font-medium truncate">{value}</p>
  </div>
);
