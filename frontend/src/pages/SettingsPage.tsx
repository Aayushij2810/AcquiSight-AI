import React, { useEffect, useState } from 'react';
import { fetchDataProviders } from '../api';
import { ProviderStatus } from '../types';

export const SettingsPage: React.FC = () => {
  const [providers, setProviders] = useState<ProviderStatus[]>([]);

  useEffect(() => {
    fetchDataProviders().then(setProviders).catch(() => {});
  }, []);

  return (
    <div className="space-y-6 fade-in-up max-w-2xl">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Settings</h1>
        <p className="text-sm text-slate-500 mt-1">Configure your AcquiSight environment.</p>
      </div>

      <div className="card space-y-4">
        <div>
          <p className="label mb-1">API URL</p>
          <p className="text-sm text-slate-300 font-mono">{process.env.REACT_APP_API_URL || 'http://localhost:8000'}</p>
        </div>
        <div>
          <p className="label mb-1">OpenAI</p>
          <p className="text-sm text-slate-400">Set OPENAI_API_KEY in backend/.env for AI memos and portfolio insights.</p>
        </div>
      </div>

      <div className="card">
        <h2 className="text-sm font-semibold text-slate-200 mb-4">Enterprise Data Providers</h2>
        <p className="text-xs text-slate-500 mb-4">
          Connect institutional feeds via environment variables — no application rewrite required.
        </p>
        <div className="space-y-2">
          {providers.map(p => (
            <div key={p.provider_id} className="flex items-center justify-between bg-surface-raised rounded-lg px-3 py-2 text-sm">
              <div>
                <p className="text-slate-200">{p.provider_label}</p>
                <p className="text-xs text-slate-500">Priority {p.priority}</p>
              </div>
              <span className={`badge border text-[10px] ${
                p.configured
                  ? 'border-green-500/30 text-green-400 bg-green-500/10'
                  : 'border-surface-border text-slate-500'
              }`}>
                {p.configured ? 'Configured' : 'Not Connected'}
              </span>
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-600 mt-4">
          Keys: BLOOMBERG_API_KEY, FACTSET_API_KEY, CAPITAL_IQ_API_KEY, FMP_API_KEY.
          Set INSTITUTIONAL_DEMO_MODE=1 for demo reference data.
        </p>
      </div>
    </div>
  );
};
