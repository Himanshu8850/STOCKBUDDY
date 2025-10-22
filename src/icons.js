// Lightweight SVG icon set (no external deps)
// Usage: <StockIcon size={24} className="nav-icon" />

import React from "react";

const base = (size) => ({
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  xmlns: "http://www.w3.org/2000/svg",
});

export const StockIcon = ({ size = 24, className = "" }) => (
  <svg {...base(size)} className={className}>
    <path
      d="M3 3v18h18"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <path
      d="M6 16l4-5 3 3 5-7"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <circle cx="18" cy="6" r="1.5" fill="currentColor" />
  </svg>
);

export const BellIcon = ({ size = 24, className = "" }) => (
  <svg {...base(size)} className={className}>
    <path d="M12 22a2 2 0 0 0 2-2H10a2 2 0 0 0 2 2z" fill="currentColor" />
    <path
      d="M18 16v-5a6 6 0 10-12 0v5l-2 2h16l-2-2z"
      stroke="currentColor"
      strokeWidth="2"
      fill="none"
      strokeLinecap="round"
    />
  </svg>
);

export const RocketIcon = ({ size = 24, className = "" }) => (
  <svg {...base(size)} className={className}>
    <path
      d="M14 10l-4 4M14.5 3.5C18 3 21 6 20.5 9.5L12 18 6 12l8.5-8.5z"
      stroke="currentColor"
      strokeWidth="2"
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M6 12s-2 5-3 6 4-1 6-3"
      stroke="currentColor"
      strokeWidth="2"
      fill="none"
      strokeLinecap="round"
    />
  </svg>
);

export const RobotIcon = ({ size = 24, className = "" }) => (
  <svg {...base(size)} className={className}>
    <rect
      x="4"
      y="7"
      width="16"
      height="11"
      rx="2"
      stroke="currentColor"
      strokeWidth="2"
      fill="none"
    />
    <circle cx="9" cy="12" r="1.5" fill="currentColor" />
    <circle cx="15" cy="12" r="1.5" fill="currentColor" />
    <path
      d="M12 4v3"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
  </svg>
);

export const AnalyticsIcon = ({ size = 24, className = "" }) => (
  <svg {...base(size)} className={className}>
    <path d="M4 20h16" stroke="currentColor" strokeWidth="2" />
    <rect x="6" y="10" width="3" height="8" rx="1" fill="currentColor" />
    <rect x="11" y="6" width="3" height="12" rx="1" fill="currentColor" />
    <rect x="16" y="13" width="3" height="5" rx="1" fill="currentColor" />
  </svg>
);

export const SearchIcon = ({ size = 20, className = "" }) => (
  <svg {...base(size)} className={className}>
    <circle
      cx="11"
      cy="11"
      r="7"
      stroke="currentColor"
      strokeWidth="2"
      fill="none"
    />
    <path
      d="M20 20l-3.5-3.5"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
  </svg>
);

export const MoneyIcon = ({ size = 20, className = "" }) => (
  <svg {...base(size)} className={className}>
    <rect
      x="3"
      y="6"
      width="18"
      height="12"
      rx="2"
      stroke="currentColor"
      strokeWidth="2"
      fill="none"
    />
    <circle cx="12" cy="12" r="2.5" fill="currentColor" />
  </svg>
);

export const RefreshIcon = ({ size = 20, className = "" }) => (
  <svg {...base(size)} className={className}>
    <path
      d="M20 6v6h-6"
      stroke="currentColor"
      strokeWidth="2"
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M20 12a8 8 0 1 1-2.34-5.66L20 6"
      stroke="currentColor"
      strokeWidth="2"
      fill="none"
      strokeLinecap="round"
    />
  </svg>
);

export const TagIcon = ({ size = 18, className = "" }) => (
  <svg {...base(size)} className={className}>
    <path
      d="M3 10l7-7h7v7l-7 7L3 10z"
      stroke="currentColor"
      strokeWidth="2"
      fill="none"
    />
    <circle cx="15" cy="6" r="1.5" fill="currentColor" />
  </svg>
);
