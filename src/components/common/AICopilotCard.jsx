import React from 'react';

const AICopilotCard = ({ children, className = '' }) => {
  return (
    <div className={`ai-insight-card p-6 border-l-4 border-l-primary shadow-[0_0_20px_rgba(192,193,255,0.08)] bg-surface-container-high/40 rounded-xl ${className}`}>
      {children}
    </div>
  );
};

export default AICopilotCard;
