import React from 'react';

const AnalyzingSVG = ({ className = '' }) => {
  return (
    <div className={`relative w-full h-full ${className}`}>
      <svg
        fill="none"
        viewBox="0 0 600 400"
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Connection Lines */}
        <g opacity="0.2">
          <path d="M100 200C100 200 200 150 300 200" stroke="#6366F1" strokeDasharray="8 8" strokeWidth="2">
            <animate attributeName="stroke-dashoffset" dur="2s" from="16" repeatCount="indefinite" to="0" />
          </path>
          <path d="M300 200C300 200 400 250 500 200" stroke="#6366F1" strokeDasharray="8 8" strokeWidth="2">
            <animate attributeName="stroke-dashoffset" dur="2s" from="16" repeatCount="indefinite" to="0" />
          </path>
        </g>
        {/* Nodes */}
        <g className="nodes">
          {/* JD Node */}
          <circle cx="100" cy="200" fill="#1E293B" r="30" stroke="#6366F1" strokeWidth="2">
            <animate attributeName="stroke-opacity" dur="3s" repeatCount="indefinite" values="0.5;1;0.5" />
          </circle>
          <path d="M92 188H108V192H92V188ZM92 196H108V200H92V196ZM92 204H102V208H92V204Z" fill="white" />
          {/* AI Core Node */}
          <circle cx="300" cy="200" fill="#1E293B" r="50" stroke="#6366F1" strokeWidth="3">
            <animate attributeName="r" dur="4s" repeatCount="indefinite" values="50;55;50" />
          </circle>
          <circle cx="300" cy="200" fill="#6366F1" fillOpacity="0.1" r="40" />
          <path d="M285 200C285 191.716 291.716 185 300 185C308.284 185 315 191.716 315 200C315 208.284 308.284 215 300 215C291.716 215 285 208.284 285 200Z" fill="#6366F1" filter="url(#glow)" />
          {/* Results Node */}
          <circle cx="500" cy="200" fill="#1E293B" r="30" stroke="#6366F1" strokeWidth="2">
            <animate attributeName="stroke-opacity" dur="3s" repeatCount="indefinite" values="0.5;1;0.5" />
          </circle>
          <path d="M492 192L498 208L508 192" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
        </g>
        <defs>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>
      </svg>
    </div>
  );
};

export default AnalyzingSVG;
