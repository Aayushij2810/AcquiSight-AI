import React from 'react';
import { scoreColor, riskColor } from '../utils';

interface Props {
  score:    number;
  label:    string;
  size?:    number;
  isRisk?:  boolean;
}

export const ScoreGauge: React.FC<Props> = ({ score, label, size = 120, isRisk = false }) => {
  const r       = (size / 2) - 10;
  const cx      = size / 2;
  const cy      = size / 2;
  const circumference = Math.PI * r;        // half-circle arc
  const dashOffset    = circumference * (1 - score / 100);
  const color   = isRisk ? riskColor(score) : scoreColor(score);
  const rotation = -180;

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size / 2 + 16} viewBox={`0 0 ${size} ${size / 2 + 16}`}>
        {/* Track */}
        <path
          d={`M ${10} ${size / 2} A ${r} ${r} 0 0 1 ${size - 10} ${size / 2}`}
          fill="none"
          stroke="#21262d"
          strokeWidth="8"
          strokeLinecap="round"
        />
        {/* Progress */}
        <path
          d={`M ${10} ${size / 2} A ${r} ${r} 0 0 1 ${size - 10} ${size / 2}`}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          style={{ transition: 'stroke-dashoffset 1s cubic-bezier(0.16,1,0.3,1)' }}
        />
        {/* Score text */}
        <text x={cx} y={size / 2 - 2} textAnchor="middle" fill={color} fontSize="22" fontWeight="600" fontFamily="Inter, sans-serif">
          {score}
        </text>
        <text x={cx} y={size / 2 + 13} textAnchor="middle" fill="#8b949e" fontSize="10" fontFamily="Inter, sans-serif">
          / 100
        </text>
      </svg>
      <span className="text-xs text-slate-400 font-medium">{label}</span>
    </div>
  );
};
