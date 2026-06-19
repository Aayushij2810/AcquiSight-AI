import type { CSSProperties } from 'react';

export const fmt = {
  usd: (v: number, decimals = 0) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: decimals,
    }).format(v),

  usdM: (v: number) => {
    if (Math.abs(v) >= 1_000_000_000) return `$${(v / 1_000_000_000).toFixed(1)}B`;
    if (Math.abs(v) >= 1_000_000)     return `$${(v / 1_000_000).toFixed(1)}M`;
    return `$${(v / 1_000).toFixed(0)}K`;
  },

  pct: (v: number, decimals = 1) => `${v.toFixed(decimals)}%`,

  num: (v: number, decimals = 1) => v.toFixed(decimals),

  multiple: (v: number | null) => v !== null ? `${v.toFixed(1)}x` : 'N/A',
};

export const scoreColor = (score: number): string => {
  if (score >= 75) return '#22c55e';
  if (score >= 55) return '#3b82f6';
  if (score >= 40) return '#eab308';
  if (score >= 25) return '#f97316';
  return '#ef4444';
};

export const riskColor = (score: number): string => {
  if (score <= 20) return '#22c55e';
  if (score <= 40) return '#3b82f6';
  if (score <= 60) return '#eab308';
  if (score <= 80) return '#f97316';
  return '#ef4444';
};

export const severityColor = (severity: string): string => {
  switch (severity.toLowerCase()) {
    case 'critical': return 'bg-red-500/15 text-red-400 border-red-500/30';
    case 'high':     return 'bg-orange-500/15 text-orange-400 border-orange-500/30';
    case 'medium':   return 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30';
    default:         return 'bg-green-500/15 text-green-400 border-green-500/30';
  }
};

export const timingColor = (score: number): string => {
  if (score >= 81) return '#22c55e';
  if (score >= 61) return '#3b82f6';
  if (score >= 41) return '#eab308';
  if (score >= 21) return '#f97316';
  return '#ef4444';
};

export const recommendationStyle = (color: string): CSSProperties => ({
  backgroundColor: `${color}18`,
  borderColor: `${color}50`,
  color,
});
