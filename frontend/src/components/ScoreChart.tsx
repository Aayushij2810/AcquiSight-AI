import React from 'react';
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar,
  ResponsiveContainer, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Cell,
} from 'recharts';
import { DimensionScores } from '../types';
import { scoreColor } from '../utils';

interface Props { scores: DimensionScores; }

export const ScoreRadar: React.FC<Props> = ({ scores }) => {
  const data = [
    { subject: 'Growth',      A: scores.growth },
    { subject: 'Profitability', A: scores.profitability },
    { subject: 'Leverage',    A: scores.leverage },
    { subject: 'Rev. Quality', A: scores.revenue_quality },
    { subject: 'Fin. Health', A: scores.financial_health },
  ];

  return (
    <div className="card fade-in-up">
      <h2 className="text-base font-semibold text-slate-200 mb-3">Score Radar</h2>
      <ResponsiveContainer width="100%" height={220}>
        <RadarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
          <PolarGrid stroke="#21262d" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#8b949e', fontSize: 11 }} />
          <Radar name="Score" dataKey="A" stroke="#2a7f8a" fill="#2a7f8a" fillOpacity={0.25} />
          <Tooltip
            contentStyle={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: '#e6edf3' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export const ScoreBar: React.FC<Props> = ({ scores }) => {
  const data = [
    { name: 'Growth',        val: scores.growth },
    { name: 'Profitability', val: scores.profitability },
    { name: 'Leverage',      val: scores.leverage },
    { name: 'Rev. Quality',  val: scores.revenue_quality },
    { name: 'Fin. Health',   val: scores.financial_health },
  ];

  return (
    <div className="card fade-in-up">
      <h2 className="text-base font-semibold text-slate-200 mb-3">Dimension Breakdown</h2>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} layout="vertical" margin={{ left: 10, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262d" horizontal={false} />
          <XAxis type="number" domain={[0, 100]} tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis dataKey="name" type="category" width={80} tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 8, fontSize: 12 }}
            formatter={(v: any) => [`${v}/100`, 'Score']}
          />
          <Bar dataKey="val" radius={[0, 4, 4, 0]}>
            {data.map((d, i) => <Cell key={i} fill={scoreColor(d.val)} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
