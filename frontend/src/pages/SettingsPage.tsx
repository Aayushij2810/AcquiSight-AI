import React, { useEffect, useState } from 'react';
import { CheckCircle2, Circle, Plug, RefreshCw, Server, Shield } from 'lucide-react';
import { fetchDataLayerStatus } from '../api';
import { DataLayerStatus, ProviderConnectionStatus } from '../types';

const badgeStyles: Record<string, string> = {
  Connected: 'border-green-500/40 text-green-400 bg-green-500/10',
  Available: 'border-brand-500/40 text-brand-300 bg-brand-500/10',
  'Not Connected': 'border-surface-border text-slate-500 bg-surface-raised',
};

const fallbackLabel: Record<string, string> = {
  ready: 'Ready',
  awaiting_credentials: 'Awaiting credentials',
  not_connected: 'Not connected',
};

export const SettingsPage: React.FC = () => {
  const [status, setStatus] = useState<DataLayerStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    fetchDataLayerStatus()
      .then(setStatus)
      .catch(() => setStatus(null))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const publicProviders = status?.providers.filter(p => p.category === 'public') ?? [];
  const enterpriseProviders = status?.providers.filter(p => p.category === 'enterprise') ?? [];

  return (
    <div className="space-y-6 fade-in-up max-w-2xl">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Settings</h1>
        <p className="text-sm text-slate-500 mt-1">Data layer configuration and provider connectivity.</p>
      </div>

      {/* Active data layer summary */}
      <div className="card space-y-4">
        <div className="flex items-center gap-2">
          <Server size={16} className="text-brand-400" />
          <h2 className="text-sm font-semibold text-slate-200">Financial Data Layer</h2>
        </div>

        {loading && <p className="text-xs text-slate-500">Loading provider status…</p>}

        {status && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <StatusTile
                label="Current Active Provider"
                value={status.active_provider.provider_label}
                icon={<CheckCircle2 size={14} className="text-green-400" />}
              />
              <StatusTile
                label="Last Successful Refresh"
                value={
                  status.last_successful_refresh
                    ? new Date(status.last_successful_refresh).toLocaleString()
                    : 'No fetch yet'
                }
                icon={<RefreshCw size={14} className="text-brand-400" />}
                sub={status.last_ticker ? `${status.last_ticker}${status.last_query ? ` · "${status.last_query}"` : ''}` : undefined}
              />
            </div>

            {status.demo_mode_note && (
              <p className="text-xs text-slate-500 bg-surface-raised rounded-lg px-3 py-2">{status.demo_mode_note}</p>
            )}

            <div>
              <p className="label mb-2">Fallback Provider Status</p>
              <div className="space-y-1">
                {status.fallback_providers.map(fp => (
                  <div key={fp.provider_id} className="flex items-center justify-between text-xs bg-surface-raised rounded-lg px-3 py-2">
                    <span className="text-slate-300">{fp.provider_label}</span>
                    <span className={`${
                      fp.status === 'ready' ? 'text-green-400' :
                      fp.status === 'awaiting_credentials' ? 'text-brand-300' : 'text-slate-500'
                    }`}>
                      {fallbackLabel[fp.status] ?? fp.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>

      {/* Public / connected feeds */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Plug size={16} className="text-green-400" />
          <h2 className="text-sm font-semibold text-slate-200">Connected Data Feeds</h2>
        </div>
        <p className="text-xs text-slate-500 mb-4">Public market data providers actively serving company intelligence.</p>
        <div className="space-y-2">
          {publicProviders.map(p => (
            <ProviderRow key={p.provider_id} provider={p} />
          ))}
        </div>
      </div>

      {/* Enterprise connectors */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Shield size={16} className="text-brand-400" />
          <h2 className="text-sm font-semibold text-slate-200">Enterprise Providers</h2>
        </div>
        <p className="text-xs text-slate-500 mb-4">
          Institutional connectors require valid API credentials. Available adapters are ready to connect — data is never attributed to these sources without credentials.
        </p>
        <div className="space-y-2">
          {enterpriseProviders.map(p => (
            <ProviderRow key={p.provider_id} provider={p} />
          ))}
        </div>
        <p className="text-xs text-slate-600 mt-4 font-mono">
          BLOOMBERG_API_KEY · FACTSET_API_KEY · CAPITAL_IQ_API_KEY · FMP_API_KEY
        </p>
      </div>

      <div className="card space-y-3">
        <p className="label">Environment</p>
        <div>
          <p className="text-xs text-slate-500 mb-1">API URL</p>
          <p className="text-sm text-slate-300 font-mono">{process.env.REACT_APP_API_URL || 'http://localhost:8000'}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500 mb-1">OpenAI</p>
          <p className="text-sm text-slate-400">Set OPENAI_API_KEY in backend/.env for AI memos and portfolio insights.</p>
        </div>
      </div>
    </div>
  );
};

const StatusTile: React.FC<{ label: string; value: string; icon: React.ReactNode; sub?: string }> = ({
  label, value, icon, sub,
}) => (
  <div className="bg-surface-raised rounded-lg p-3">
    <p className="label mb-1 flex items-center gap-1.5">{icon}{label}</p>
    <p className="text-sm font-medium text-slate-200">{value}</p>
    {sub && <p className="text-[10px] text-slate-500 mt-0.5">{sub}</p>}
  </div>
);

const ProviderRow: React.FC<{ provider: ProviderConnectionStatus }> = ({ provider: p }) => (
  <div className="flex items-center justify-between bg-surface-raised rounded-lg px-3 py-2.5 text-sm gap-3">
    <div className="min-w-0">
      <p className="text-slate-200">{p.provider_label}</p>
      <p className="text-xs text-slate-500 truncate">{p.subtitle}</p>
      {p.credential_env_var && p.connection_state !== 'connected' && (
        <p className="text-[10px] text-slate-600 font-mono mt-0.5">{p.credential_env_var}</p>
      )}
      {p.last_successful_refresh && (
        <p className="text-[10px] text-slate-600 mt-0.5">
          Last refresh: {new Date(p.last_successful_refresh).toLocaleString()}
        </p>
      )}
    </div>
    <span className={`badge border text-[10px] shrink-0 flex items-center gap-1 ${badgeStyles[p.badge] ?? badgeStyles['Not Connected']}`}>
      {p.badge === 'Connected' && <CheckCircle2 size={10} />}
      {p.badge === 'Available' && <Circle size={10} />}
      {p.badge}
    </span>
  </div>
);
