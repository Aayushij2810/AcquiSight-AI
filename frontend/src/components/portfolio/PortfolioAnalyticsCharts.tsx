import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, ScatterChart, Scatter, ZAxis,
} from 'recharts';
import { PortfolioAnalytics } from '../../types';

const COLORS = ['#2a7f8a', '#3b82f6', '#22c55e', '#eab308', '#f97316', '#ef4444'];

interface Props { analytics: PortfolioAnalytics | null }

export const PortfolioAnalyticsCharts: React.FC<Props> = ({ analytics }) => {
  if (!analytics || analytics.total_opportunities === 0) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
      <ChartCard title="Investment Score Distribution">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={analytics.investment_score_distribution}>
            <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
            <XAxis dataKey="label" tick={{ fill: '#8b949e', fontSize: 11 }} />
            <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} />
            <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #21262d', fontSize: 12 }} />
            <Bar dataKey="count" fill="#2a7f8a" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Risk Score Distribution">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={analytics.risk_score_distribution}>
            <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
            <XAxis dataKey="label" tick={{ fill: '#8b949e', fontSize: 11 }} />
            <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} />
            <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #21262d', fontSize: 12 }} />
            <Bar dataKey="count" fill="#f97316" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Industry Breakdown">
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie data={analytics.industry_breakdown} dataKey="count" nameKey="industry" cx="50%" cy="50%" outerRadius={70} label={({ industry, percent }) => `${industry} ${(percent * 100).toFixed(0)}%`}>
              {analytics.industry_breakdown.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #21262d', fontSize: 12 }} />
          </PieChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Pipeline Stage Breakdown">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={analytics.stage_breakdown} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#21262d" horizontal={false} />
            <XAxis type="number" tick={{ fill: '#8b949e', fontSize: 11 }} />
            <YAxis dataKey="stage" type="category" width={120} tick={{ fill: '#8b949e', fontSize: 10 }} />
            <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #21262d', fontSize: 12 }} />
            <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Growth vs Risk (bubble = investment score)">
        <ResponsiveContainer width="100%" height={220}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
            <XAxis dataKey="growth_rate" name="Growth %" tick={{ fill: '#8b949e', fontSize: 11 }} />
            <YAxis dataKey="risk_score" name="Risk" tick={{ fill: '#8b949e', fontSize: 11 }} />
            <ZAxis dataKey="investment_score" range={[40, 400]} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ background: '#161b22', border: '1px solid #21262d', fontSize: 12 }} />
            <Scatter data={analytics.growth_risk_scatter} fill="#2a7f8a" />
          </ScatterChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Portfolio Highlights">
        <div className="space-y-2 text-xs">
          {([
            ['Best Opportunity', analytics.highlights.best_opportunity],
            ['Safest Investment', analytics.highlights.safest_investment],
            ['Highest Growth', analytics.highlights.highest_growth],
            ['Most Undervalued (EV/EBITDA)', analytics.highlights.most_undervalued],
          ] as const).map(([label, h]) => h ? (
            <div key={label} className="flex justify-between bg-surface-raised rounded-lg px-3 py-2">
              <span className="text-slate-500">{label}</span>
              <span className="text-slate-200 font-medium">{h.company_name}</span>
            </div>
          ) : null)}
        </div>
      </ChartCard>
    </div>
  );
};

const ChartCard: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="card">
    <h3 className="text-sm font-semibold text-slate-200 mb-3">{title}</h3>
    {children}
  </div>
);
