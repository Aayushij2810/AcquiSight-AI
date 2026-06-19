import React from 'react';

export const SettingsPage: React.FC = () => (
  <div className="space-y-6 fade-in-up max-w-lg">
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
        <p className="text-sm text-slate-400">Configure <code className="text-brand-400">OPENAI_API_KEY</code> in <code className="text-slate-300">backend/.env</code> for AI memos and portfolio insights.</p>
      </div>
      <div>
        <p className="label mb-1">Database</p>
        <p className="text-sm text-slate-400">Portfolio data is stored in PostgreSQL (<code className="text-slate-300">investment_opportunities</code> table).</p>
      </div>
    </div>
  </div>
);
