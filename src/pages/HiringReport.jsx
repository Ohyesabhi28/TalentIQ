import React from 'react';
import { Link } from 'react-router-dom';
import GlassCard from '../components/common/GlassCard';
import AICopilotCard from '../components/common/AICopilotCard';
import mockData from '../data/mockData.json';

const HiringReport = ({ candidates }) => {
  const reportData = mockData.summaryReport;
  const activeCandidates = (candidates && candidates.length > 0) ? candidates : mockData.candidates;

  // Calculate dynamic fit ratios based on active candidates list
  const strongCount = activeCandidates.filter((c) => c.score >= 90).length;
  const goodCount = activeCandidates.filter((c) => c.score >= 80 && c.score < 90).length;
  const averageCount = activeCandidates.filter((c) => c.score < 80).length;

  const total = activeCandidates.length;

  // Conic gradient style calculated dynamically based on scores
  const strongRatio = total > 0 ? (strongCount / total) * 100 : 0;
  const goodRatio = total > 0 ? (goodCount / total) * 100 : 0;
  const averageRatio = total > 0 ? (averageCount / total) * 100 : 0;

  const conicGradientStyle = {
    background: `conic-gradient(
      #c0c1ff 0% ${strongRatio}%,
      #ffb783 ${strongRatio}% ${strongRatio + goodRatio}%,
      #bec6e0 ${strongRatio + goodRatio}% 100%
    )`
  };

  return (
    <div className="space-y-8">
      {/* Dossier Header */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <Link
            to="/results"
            className="inline-flex items-center text-primary font-label-sm text-label-sm mb-2 hover:underline"
          >
            <span className="material-symbols-outlined text-[16px] mr-1">arrow_back</span>
            Back to pipeline results
          </Link>
          <h2 className="text-headline-lg font-bold text-on-surface tracking-tight">AI Hiring &amp; Sourcing Report</h2>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => window.print()}
            className="btn-primary px-5 py-2.5 rounded-lg font-label-md text-label-md cursor-pointer flex items-center gap-2 active:scale-95 transition-transform glow-btn"
          >
            <span className="material-symbols-outlined text-[18px]">print</span> Print Report
          </button>
        </div>
      </header>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
        {/* Left Column: Executive Summary & Details */}
        <div className="lg:col-span-8 space-y-6">
          <GlassCard className="p-6 md:p-8 space-y-6">
            <h3 className="font-headline-md text-headline-md text-white">Executive Summary</h3>
            <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed font-light">
              This dossier summarizes the semantic analysis of candidates evaluated for the **{mockData.jobDescription.title}** role. Our AI Sourcing Agent evaluated **{total} profiles** against core specifications ({mockData.jobDescription.requiredSkills.join(', ')}).
            </p>

            <div className="space-y-4 pt-4 border-t border-white/5">
              <h4 className="font-bold text-white text-base">Key Sourcing Highlights</h4>
              <ul className="list-disc pl-5 space-y-3 text-sm text-on-surface-variant leading-relaxed font-light">
                {reportData.highlights.map((highlight, index) => (
                  <li key={index}>
                    {highlight.split('**').map((part, i) => i % 2 === 1 ? <strong key={i} className="text-white">{part}</strong> : part)}
                  </li>
                ))}
              </ul>
            </div>
          </GlassCard>

          {/* Detailed Candidate Breakdown table */}
          <GlassCard className="p-6 md:p-8">
            <h3 className="font-headline-md text-headline-md text-white mb-6">Pipeline Scorecards</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/10 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider">
                    <th className="pb-3">Candidate</th>
                    <th className="pb-3 text-center">Score</th>
                    <th className="pb-3 text-center">Ranking</th>
                    <th className="pb-3 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="font-body-md text-body-md divide-y divide-white/5">
                  {activeCandidates.map((candidate) => (
                    <tr key={candidate.id} className="hover:bg-white/5 transition-colors">
                      <td className="py-4 font-semibold text-white flex items-center gap-3">
                        <img
                          src={candidate.avatar}
                          className="w-8 h-8 rounded-full object-cover"
                          alt={candidate.name}
                        />
                        {candidate.name}
                      </td>
                      <td className="py-4 text-center font-headline font-bold text-primary">
                        {candidate.score}%
                      </td>
                      <td className="py-4 text-center text-on-surface-variant">
                        {candidate.ranking}
                      </td>
                      <td className="py-4 text-right">
                        <span className="px-2.5 py-0.5 rounded-full font-label-sm text-label-sm font-bold uppercase tag-green">
                          {candidate.matchType}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCard>
        </div>

        {/* Right Column: Visual Conic chart & Stats */}
        <div className="lg:col-span-4 space-y-6 flex flex-col">
          {/* Conic Gradient Pie Chart Card */}
          <GlassCard className="p-6 md:p-8 flex flex-col items-center justify-center text-center space-y-6 flex-grow">
            <h3 className="font-headline-md text-headline-md text-white">Sourcing Fit Ratios</h3>
            
            <div className="relative w-48 h-48 flex items-center justify-center">
              <div 
                className="w-full h-full rounded-full shadow-[0_0_30px_rgba(192,193,255,0.1)] transition-all duration-500" 
                style={conicGradientStyle}
              ></div>
              {/* Inner cutout for donut chart effect */}
              <div className="absolute w-32 h-32 rounded-full bg-surface-container-lowest flex items-center justify-center">
                <div className="text-center">
                  <div className="text-3xl font-black text-white">{total}</div>
                  <div className="text-[10px] text-on-surface-variant uppercase font-bold tracking-widest mt-0.5">
                    Profiles Scored
                  </div>
                </div>
              </div>
            </div>

            {/* Legend */}
            <div className="w-full space-y-2.5 pt-4 border-t border-white/5 text-left text-xs font-semibold">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-[#c0c1ff]"></div>
                  <span className="text-on-surface-variant">Strong Fit (&gt;90%)</span>
                </div>
                <span className="text-white">{strongCount} ({total > 0 ? Math.round((strongCount / total) * 100) : 0}%)</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-[#ffb783]"></div>
                  <span className="text-on-surface-variant">Good Fit (80-89%)</span>
                </div>
                <span className="text-white">{goodCount} ({total > 0 ? Math.round((goodCount / total) * 100) : 0}%)</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-[#bec6e0]"></div>
                  <span className="text-on-surface-variant">Average Fit (70-79%)</span>
                </div>
                <span className="text-white">{averageCount} ({total > 0 ? Math.round((averageCount / total) * 100) : 0}%)</span>
              </div>
            </div>
          </GlassCard>

          {/* AI Copilot Suggestion Card */}
          <AICopilotCard className="shrink-0">
            <div className="flex gap-3 items-start">
              <span className="material-symbols-outlined text-primary text-xl">lightbulb</span>
              <div className="space-y-1">
                <h4 className="font-bold text-white text-sm">Next Step Recommendation</h4>
                <p className="text-xs text-on-surface-variant leading-relaxed font-light">
                  {reportData.recommendation}
                </p>
              </div>
            </div>
          </AICopilotCard>
        </div>
      </div>
    </div>
  );
};

export default HiringReport;
