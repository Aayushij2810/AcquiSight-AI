import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Bot, Loader2, Send, Sparkles, User } from 'lucide-react';
import { sendCopilotMessage } from '../api';
import { CopilotChatResponse, CopilotSourceMetric } from '../types';

const CATEGORY_COLORS: Record<string, string> = {
  'Portfolio Data': 'text-violet-400 bg-violet-500/10 border-violet-500/25',
  'Investment Scores': 'text-brand-300 bg-brand-500/10 border-brand-500/25',
  'Risk Scores': 'text-red-400 bg-red-500/10 border-red-500/25',
  'Valuation Metrics': 'text-emerald-400 bg-emerald-500/10 border-emerald-500/25',
  'Historical Trends': 'text-blue-400 bg-blue-500/10 border-blue-500/25',
  'Timing Scores': 'text-amber-400 bg-amber-500/10 border-amber-500/25',
};

const renderInline = (text: string): React.ReactNode[] => {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="text-slate-100 font-semibold">{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
      return <em key={i} className="text-slate-400">{part.slice(1, -1)}</em>;
    }
    return part;
  });
};

const MarkdownTable: React.FC<{ rows: string[][] }> = ({ rows }) => (
  <div className="overflow-x-auto my-2 rounded-lg border border-surface-border">
    <table className="w-full text-xs">
      <tbody>
        {rows.map((row, ri) => (
          <tr key={ri} className={ri === 0 ? 'bg-surface-raised/80 text-slate-300' : 'border-t border-surface-border/40 text-slate-400'}>
            {row.map((cell, ci) => (
              <td key={ci} className="px-3 py-2 whitespace-nowrap">{renderInline(cell.trim())}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const parseTableRows = (lines: string[], start: number): { rows: string[][]; end: number } => {
  const rows: string[][] = [];
  let i = start;
  while (i < lines.length && lines[i].trim().startsWith('|')) {
    const cells = lines[i].trim().split('|').slice(1, -1).map(c => c.trim());
    if (cells.length && !cells.every(c => /^[-:]+$/.test(c))) {
      rows.push(cells);
    }
    i += 1;
  }
  return { rows, end: i };
};

const AnswerText: React.FC<{ content: string }> = ({ content }) => {
  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const trimmed = lines[i].trim();

    if (!trimmed) {
      elements.push(<div key={i} className="h-1.5" />);
      i += 1;
      continue;
    }

    if (trimmed.startsWith('|')) {
      const { rows, end } = parseTableRows(lines, i);
      if (rows.length > 0) {
        elements.push(<MarkdownTable key={i} rows={rows} />);
        i = end;
        continue;
      }
    }

    if (trimmed.startsWith('#### ')) {
      elements.push(<h4 key={i} className="text-sm font-semibold text-slate-200 mt-3 mb-1">{renderInline(trimmed.slice(5))}</h4>);
    } else if (trimmed.startsWith('### ')) {
      elements.push(<h3 key={i} className="text-sm font-semibold text-slate-100 mt-3 mb-1">{renderInline(trimmed.slice(4))}</h3>);
    } else if (trimmed.startsWith('## ')) {
      elements.push(<h2 key={i} className="text-base font-semibold text-slate-100 mt-3 mb-1">{renderInline(trimmed.slice(3))}</h2>);
    } else if (/^\d+\.\s/.test(trimmed)) {
      elements.push(
        <p key={i} className="pl-1 flex gap-2">
          <span className="text-brand-400 shrink-0">{trimmed.match(/^\d+/)?.[0]}.</span>
          <span>{renderInline(trimmed.replace(/^\d+\.\s/, ''))}</span>
        </p>,
      );
    } else if (trimmed.startsWith('- ')) {
      elements.push(
        <p key={i} className="pl-3 flex gap-2">
          <span className="text-brand-400 shrink-0">•</span>
          <span>{renderInline(trimmed.slice(2))}</span>
        </p>,
      );
    } else {
      elements.push(<p key={i}>{renderInline(trimmed)}</p>);
    }

    i += 1;
  }

  return <div className="space-y-1">{elements}</div>;
};

const SUGGESTIONS = [
  'Why does NVIDIA score higher than Microsoft?',
  'Compare Meta vs Alphabet',
  'What are the biggest risks for Tesla?',
  'Which company in my portfolio has the highest risk-adjusted return?',
];

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  meta?: CopilotChatResponse;
}

const SourceMetrics: React.FC<{ sources: CopilotSourceMetric[]; groundedIn: string[] }> = ({ sources, groundedIn }) => (
  <div className="mt-4 space-y-3">
    <div className="flex flex-wrap gap-1.5">
      {groundedIn.map(layer => (
        <span key={layer} className="text-[10px] px-2 py-0.5 rounded-full border border-surface-border text-slate-500 bg-surface-raised">
          {layer}
        </span>
      ))}
    </div>
    {sources.length > 0 && (
      <div className="rounded-lg border border-surface-border bg-surface/60 overflow-hidden">
        <div className="px-3 py-2 border-b border-surface-border/60 bg-surface-raised/50">
          <p className="text-[10px] font-medium uppercase tracking-wider text-slate-500">Source Metrics</p>
        </div>
        <div className="divide-y divide-surface-border/40 max-h-56 overflow-y-auto">
          {sources.map((s, i) => {
            const color = CATEGORY_COLORS[s.category] ?? 'text-slate-400 bg-slate-500/10 border-slate-500/25';
            return (
              <div key={i} className="px-3 py-2.5 flex gap-3 items-start text-xs">
                <span className={`shrink-0 px-1.5 py-0.5 rounded border text-[10px] font-medium ${color}`}>
                  {s.category}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-slate-300 font-medium">{s.label}</p>
                  <p className="text-slate-500 mt-0.5 break-words">{s.value}</p>
                  {s.company && <p className="text-[10px] text-brand-400/80 mt-0.5">{s.company}</p>}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    )}
  </div>
);

export const CopilotPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: 'user', content: trimmed };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const result = await sendCopilotMessage(trimmed);
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: result.answer,
        meta: result,
      }]);
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      const errText = typeof msg === 'string' ? msg : 'Copilot failed to respond. Please try again.';
      setError(errText);
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `**Unable to complete analysis.** ${errText}`,
      }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [loading]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] max-h-[820px] fade-in-up">
      {/* Header */}
      <div className="shrink-0 border border-surface-border bg-gradient-to-r from-surface-card via-surface-raised to-surface-card rounded-xl px-5 py-4 mb-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-brand-500/15 border border-brand-500/30 flex items-center justify-center">
            <Sparkles size={18} className="text-brand-400" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-slate-100">AcquiSight Copilot</h1>
            <p className="text-xs text-slate-500">Grounded in your portfolio, scores, risk, valuation & timing data</p>
          </div>
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col min-h-0 border border-surface-border rounded-xl bg-surface-card overflow-hidden">
        <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 space-y-6">
          {isEmpty && (
            <div className="flex flex-col items-center justify-center h-full text-center px-4 py-8">
              <div className="w-14 h-14 rounded-2xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center mb-4">
                <Bot size={28} className="text-brand-400" />
              </div>
              <h2 className="text-base font-medium text-slate-200 mb-1">Ask anything about your investments</h2>
              <p className="text-sm text-slate-500 max-w-md mb-6">
                Answers are generated exclusively from AcquiSight scores, risk models, valuation comps, historical trends, and your portfolio.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-2xl">
                {SUGGESTIONS.map(s => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => send(s)}
                    className="text-left text-sm px-4 py-3 rounded-lg border border-surface-border bg-surface-raised/50 text-slate-400 hover:text-slate-200 hover:border-brand-500/30 hover:bg-brand-500/5 transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map(msg => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`shrink-0 w-8 h-8 rounded-lg flex items-center justify-center mt-0.5 ${
                msg.role === 'assistant'
                  ? 'bg-brand-500/15 border border-brand-500/25'
                  : 'bg-slate-700/50 border border-surface-border'
              }`}>
                {msg.role === 'assistant'
                  ? <Bot size={16} className="text-brand-400" />
                  : <User size={16} className="text-slate-400" />}
              </div>
              <div className={`max-w-[85%] sm:max-w-[75%] ${msg.role === 'user' ? 'text-right' : ''}`}>
                <div
                  className={`rounded-2xl px-4 py-3 text-sm leading-relaxed text-left ${
                    msg.role === 'user'
                      ? 'bg-brand-600/20 border border-brand-500/30 text-slate-100'
                      : 'bg-surface-raised border border-surface-border text-slate-200'
                  }`}
                >
                  {msg.role === 'assistant' ? (
                    <AnswerText content={msg.content} />
                  ) : (
                    msg.content
                  )}
                </div>
                {msg.meta && (
                  <SourceMetrics sources={msg.meta.sources} groundedIn={msg.meta.grounded_in} />
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-3">
              <div className="shrink-0 w-8 h-8 rounded-lg bg-brand-500/15 border border-brand-500/25 flex items-center justify-center">
                <Bot size={16} className="text-brand-400" />
              </div>
              <div className="rounded-2xl px-4 py-3 bg-surface-raised border border-surface-border flex items-center gap-2 text-sm text-slate-500">
                <Loader2 size={16} className="animate-spin text-brand-400" />
                Analyzing AcquiSight data…
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/5 px-4 py-3 text-sm text-red-400">
              {error}
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input bar */}
        <div className="shrink-0 border-t border-surface-border bg-surface/80 backdrop-blur-sm px-4 sm:px-6 py-4">
          <div className="flex gap-2 items-end max-w-3xl mx-auto">
            <textarea
              ref={inputRef}
              className="input flex-1 min-h-[44px] max-h-32 resize-none py-2.5"
              placeholder="Ask about scores, risks, comparisons, or your portfolio…"
              rows={1}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button
              type="button"
              className="btn-primary shrink-0 h-[44px] px-4"
              onClick={() => send(input)}
              disabled={loading || !input.trim()}
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
            </button>
          </div>
          <p className="text-[10px] text-slate-600 text-center mt-2">
            Copilot uses AcquiSight data only · Not investment advice
          </p>
        </div>
      </div>
    </div>
  );
};
