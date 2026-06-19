import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import { BarChart3, Loader2, Search, TrendingUp } from 'lucide-react';
import { fetchHistoricalTrends, searchCompanies } from '../api';
import { CompanySearchMatch, HistoricalTrends } from '../types';
import { currencySymbol, fmtMoney, fmtMoneyCompact } from '../utils';

const CHART_TOOLTIP = {
  background: '#0d1117',
  border: '1px solid #30363d',
  borderRadius: 8,
  fontSize: 12,
  color: '#e6edf3',
};

const fmtPct = (v: number) => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%`;

const billionsLabel = (currency: string) =>
  `Annual (${currency} billions)`;

const priceLabel = (currency: string) =>
  `Year-end closing price (${currency})`;

export const HistoricalAnalysisPage: React.FC = () => {
  const [query, setQuery] = useState('Microsoft');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<HistoricalTrends | null>(null);
  const [autocomplete, setAutocomplete] = useState<CompanySearchMatch[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const load = useCallback(async (q: string) => {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const result = await fetchHistoricalTrends(q.trim());
      setData(result);
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(typeof msg === 'string' ? msg : 'Failed to load historical trends.');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load('Microsoft');
  }, [load]);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    const q = query.trim();
    if (q.length < 2) { setAutocomplete([]); return; }
    debounceRef.current = setTimeout(async () => {
      try {
        const res = await searchCompanies(q, 6);
        setAutocomplete(res.results);
        setShowDropdown(res.results.length > 0);
      } catch { setAutocomplete([]); }
    }, 280);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [query]);

  const chartData = (data?.years ?? []).map(y => ({
    ...y,
    revenueB: y.revenue ? y.revenue / 1e9 : null,
    ebitdaB: y.ebitda ? y.ebitda / 1e9 : null,
  }));

  const currency = data?.currency ?? 'USD';
  const sym = currencySymbol(currency);
  const fmtBillions = (v: number) => `${sym}${v.toFixed(1)}B`;

  return (
    <div className="space-y-6 fade-in-up">
      {/* Header band — Capital IQ style */}
      <div className="border border-surface-border bg-gradient-to-r from-surface-card to-surface-raised rounded-xl px-5 py-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <BarChart3 size={18} className="text-brand-400" />
              <h1 className="text-lg font-semibold text-slate-100">Historical Analysis</h1>
            </div>
            <p className="text-xs text-slate-500">5-year financial trends · Revenue · EBITDA · Growth · Share Price</p>
          </div>
          {data && (
            <div className="text-right">
              <p className="text-sm font-medium text-slate-200">{data.company_name}</p>
              <p className="text-xs text-brand-400 font-mono">{data.ticker} · {data.period_label}</p>
              <p className="text-[10px] text-slate-500 mt-0.5">Figures in {data.currency}</p>
            </div>
          )}
        </div>
      </div>

      {/* Search */}
      <div className="card relative">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <input
              className="input w-full"
              placeholder="Microsoft, MSFT, Adobe…"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), load(query), setShowDropdown(false))}
              onFocus={() => autocomplete.length > 0 && setShowDropdown(true)}
            />
            {showDropdown && autocomplete.length > 0 && (
              <ul className="absolute z-20 top-full left-0 right-0 mt-1 bg-surface-raised border border-slate-700 rounded-lg shadow-xl max-h-48 overflow-y-auto">
                {autocomplete.map(m => (
                  <li key={m.ticker}>
                    <button
                      type="button"
                      className="w-full text-left px-3 py-2 text-sm hover:bg-brand-500/10 flex justify-between"
                      onClick={() => { setQuery(m.company_name); setShowDropdown(false); load(m.ticker); }}
                    >
                      <span className="text-slate-200 truncate">{m.company_name}</span>
                      <span className="text-brand-400 font-mono text-xs">{m.ticker}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <button type="button" className="btn-primary shrink-0" onClick={() => load(query)} disabled={loading}>
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
            Analyze
          </button>
        </div>
      </div>

      {error && !loading && (
        <div className="card border-red-500/30 bg-red-500/5 p-4">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {loading && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[...Array(4)].map((_, i) => <div key={i} className="card skeleton h-20" />)}
        </div>
      )}

      {data && !loading && (
        <>
          {/* KPI strip */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <KpiCard label="Revenue CAGR" value={data.metrics.revenue_cagr != null ? fmtPct(data.metrics.revenue_cagr) : '—'} accent="text-brand-300" />
            <KpiCard label="EBITDA CAGR" value={data.metrics.ebitda_cagr != null ? fmtPct(data.metrics.ebitda_cagr) : '—'} accent="text-emerald-400" />
            <KpiCard label="Growth Consistency" value={`${data.metrics.growth_consistency_score}/100`} sub="Higher = more stable growth" accent="text-blue-400" />
            <KpiCard label="Revenue Volatility" value={`${data.metrics.revenue_volatility}%`} sub={`EBITDA σ ${data.metrics.ebitda_volatility}%`} accent="text-amber-400" />
          </div>

          <p className="text-[10px] text-slate-600">
            Source: {data.data_source} · Updated {new Date(data.last_updated).toLocaleString()}
          </p>

          {/* Charts 2x2 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <TrendChart title="Revenue Trend" subtitle={billionsLabel(currency)}>
              <ResponsiveContainer width="100%" height={240}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#2a7f8a" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="#2a7f8a" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#21262d" vertical={false} />
                  <XAxis dataKey="label" tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={{ stroke: '#30363d' }} />
                  <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickFormatter={fmtBillions} />
                  <Tooltip contentStyle={CHART_TOOLTIP} formatter={(v: number) => [fmtBillions(v), 'Revenue']} />
                  <Area type="monotone" dataKey="revenueB" stroke="#2a7f8a" fill="url(#revGrad)" strokeWidth={2} dot={{ r: 3, fill: '#2a7f8a' }} />
                </AreaChart>
              </ResponsiveContainer>
            </TrendChart>

            <TrendChart title="EBITDA Trend" subtitle={billionsLabel(currency)}>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#21262d" vertical={false} />
                  <XAxis dataKey="label" tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={{ stroke: '#30363d' }} />
                  <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickFormatter={fmtBillions} />
                  <Tooltip contentStyle={CHART_TOOLTIP} formatter={(v: number) => [fmtBillions(v), 'EBITDA']} />
                  <Bar dataKey="ebitdaB" fill="#22c55e" radius={[4, 4, 0, 0]} opacity={0.85} />
                </BarChart>
              </ResponsiveContainer>
            </TrendChart>

            <TrendChart title="Revenue Growth Trend" subtitle="Year-over-year revenue growth">
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={chartData.filter(d => d.revenue_growth != null)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#21262d" vertical={false} />
                  <XAxis dataKey="label" tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={{ stroke: '#30363d' }} />
                  <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickFormatter={v => `${v}%`} />
                  <Tooltip contentStyle={CHART_TOOLTIP} formatter={(v: number) => [fmtPct(v), 'YoY Growth']} />
                  <Line type="monotone" dataKey="revenue_growth" stroke="#3b82f6" strokeWidth={2.5} dot={{ r: 4, fill: '#3b82f6' }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </TrendChart>

            <TrendChart title="Share Price Trend" subtitle={priceLabel(currency)}>
              <ResponsiveContainer width="100%" height={240}>
                <AreaChart data={chartData.filter(d => d.stock_price != null)}>
                  <defs>
                    <linearGradient id="pxGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#a78bfa" stopOpacity={0.35} />
                      <stop offset="100%" stopColor="#a78bfa" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#21262d" vertical={false} />
                  <XAxis dataKey="label" tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={{ stroke: '#30363d' }} />
                  <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickFormatter={v => fmtMoney(v, currency, 0)} domain={['auto', 'auto']} />
                  <Tooltip contentStyle={CHART_TOOLTIP} formatter={(v: number) => [fmtMoney(v, currency), 'Close']} />
                  <Area type="monotone" dataKey="stock_price" stroke="#a78bfa" fill="url(#pxGrad)" strokeWidth={2} dot={{ r: 3, fill: '#a78bfa' }} />
                </AreaChart>
              </ResponsiveContainer>
            </TrendChart>
          </div>

          {/* Data table — Bloomberg-style */}
          <div className="card overflow-x-auto">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp size={14} className="text-brand-400" />
              <h3 className="text-sm font-semibold text-slate-200">Historical Financial Summary</h3>
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-slate-500 border-b border-surface-border">
                  <th className="py-2 pr-4 font-medium">Period</th>
                  <th className="py-2 pr-4 font-medium text-right">Revenue</th>
                  <th className="py-2 pr-4 font-medium text-right">EBITDA</th>
                  <th className="py-2 pr-4 font-medium text-right">Rev Growth</th>
                  <th className="py-2 font-medium text-right">Share Price</th>
                </tr>
              </thead>
              <tbody>
                {data.years.map(row => (
                  <tr key={row.year} className="border-b border-surface-border/50 hover:bg-surface-raised/50">
                    <td className="py-2.5 pr-4 text-slate-300 font-medium">{row.label}</td>
                    <td className="py-2.5 pr-4 text-right tabular-nums text-slate-200">{row.revenue ? fmtMoneyCompact(row.revenue, currency) : '—'}</td>
                    <td className="py-2.5 pr-4 text-right tabular-nums text-slate-200">{row.ebitda ? fmtMoneyCompact(row.ebitda, currency) : '—'}</td>
                    <td className="py-2.5 pr-4 text-right tabular-nums text-brand-300">
                      {row.revenue_growth != null ? fmtPct(row.revenue_growth) : '—'}
                    </td>
                    <td className="py-2.5 text-right tabular-nums text-slate-200">
                      {row.stock_price != null ? fmtMoney(row.stock_price, currency) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

const KpiCard: React.FC<{ label: string; value: string; sub?: string; accent: string }> = ({ label, value, sub, accent }) => (
  <div className="card border-surface-border">
    <p className="label mb-1">{label}</p>
    <p className={`text-2xl font-semibold tabular-nums ${accent}`}>{value}</p>
    {sub && <p className="text-[10px] text-slate-600 mt-1">{sub}</p>}
  </div>
);

const TrendChart: React.FC<{ title: string; subtitle: string; children: React.ReactNode }> = ({ title, subtitle, children }) => (
  <div className="card border-surface-border">
    <div className="mb-4 border-b border-surface-border/60 pb-3">
      <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
      <p className="text-[10px] text-slate-500 mt-0.5">{subtitle}</p>
    </div>
    {children}
  </div>
);
