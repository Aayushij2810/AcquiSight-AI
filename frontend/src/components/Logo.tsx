import React from 'react';

export const Logo: React.FC<{ size?: number }> = ({ size = 32 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 32 32"
    fill="none"
    aria-label="AcquiSight AI logo"
    xmlns="http://www.w3.org/2000/svg"
  >
    {/* Outer ring */}
    <circle cx="16" cy="16" r="15" stroke="#2a7f8a" strokeWidth="1.5" />
    {/* Chart bars */}
    <rect x="7"  y="20" width="4" height="5" rx="1" fill="#2a7f8a" opacity="0.5" />
    <rect x="13" y="14" width="4" height="11" rx="1" fill="#2a7f8a" opacity="0.75" />
    <rect x="19" y="9"  width="4" height="16" rx="1" fill="#2a7f8a" />
    {/* Trend line */}
    <polyline
      points="9,20 15,14 21,9"
      stroke="#6bb8c0"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    {/* Dot at peak */}
    <circle cx="21" cy="9" r="2" fill="#6bb8c0" />
  </svg>
);
