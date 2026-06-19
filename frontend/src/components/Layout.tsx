import React from 'react';
import { LayoutDashboard, Search, Briefcase, Settings, Github } from 'lucide-react';
import { Logo } from './Logo';
import { AppView } from '../types';

interface Props {
  view: AppView;
  onNavigate: (view: AppView) => void;
  children: React.ReactNode;
}

const NAV: { id: AppView; label: string; icon: React.ReactNode }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={15} /> },
  { id: 'screen',    label: 'Screen Company', icon: <Search size={15} /> },
  { id: 'portfolio', label: 'Portfolio Mode', icon: <Briefcase size={15} /> },
  { id: 'settings',  label: 'Settings', icon: <Settings size={15} /> },
];

export const Layout: React.FC<Props> = ({ view, onNavigate, children }) => (
  <div className="min-h-screen bg-surface text-slate-200 flex flex-col">
    <header className="border-b border-surface-border sticky top-0 z-30 bg-surface/90 backdrop-blur-sm">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Logo size={28} />
          <div>
            <span className="font-semibold text-slate-100 text-sm">AcquiSight AI</span>
            <span className="hidden sm:inline text-slate-500 text-xs ml-2">Investment Intelligence Platform</span>
          </div>
        </div>
        <a
          href="https://github.com/Aayushij2810/AcquiSight-AI"
          target="_blank"
          rel="noopener noreferrer"
          className="btn-ghost hidden sm:flex"
        >
          <Github size={14} /> GitHub
        </a>
      </div>
      <nav className="border-t border-surface-border/60">
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 flex gap-1 overflow-x-auto">
          {NAV.map(item => (
            <button
              key={item.id}
              type="button"
              onClick={() => onNavigate(item.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                view === item.id
                  ? 'border-brand-400 text-brand-300'
                  : 'border-transparent text-slate-500 hover:text-slate-300'
              }`}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </div>
      </nav>
    </header>

    <main className="flex-1 max-w-screen-2xl mx-auto w-full px-4 sm:px-6 py-6">
      {children}
    </main>

    <footer className="border-t border-surface-border mt-auto">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <p className="text-xs text-slate-600">AcquiSight AI — For informational purposes only. Not investment advice.</p>
        <p className="text-xs text-slate-600">Built with React · FastAPI · OpenAI</p>
      </div>
    </footer>
  </div>
);
