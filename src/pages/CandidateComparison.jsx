import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import GlassCard from '../components/common/GlassCard';
import mockData from '../data/mockData.json';

const CandidateComparison = ({ candidates }) => {
  const navigate = useNavigate();

  // Fallback to all mock candidates if no active profiles are in state
  const compareList = (candidates && candidates.length >= 2) ? candidates : mockData.candidates;

  const getScoreColorClass = (score) => {
    if (score >= 90) return 'tag-green text-glow';
    if (score >= 80) return 'text-[#34d399] bg-[#10b981]/15 border border-[#10b981]/20';
    return 'text-[#f87171] bg-[#ef4444]/15 border border-[#ef4444]/20';
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
            Back to Pipeline
          </Link>
          <h2 className="text-headline-lg font-bold text-on-surface tracking-tight">Candidate Comparison Matrix</h2>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => window.print()}
            className="px-4 py-2 rounded-lg bg-surface-container-high border border-white/10 hover:border-white/40 hover:bg-white/5 transition-colors font-label-md text-label-md text-on-surface flex items-center gap-2 cursor-pointer active:scale-95"
          >
            <span className="material-symbols-outlined text-[18px]">download</span> Export PDF Report
          </button>
        </div>
      </header>

      {/* Comparison Grid Scroll Container */}
      <div className="glass-card overflow-x-auto shadow-lg border border-white/10">
        <div className="min-w-[900px]">
          {/* Header Row */}
          <div className="grid grid-cols-4 border-b border-white/10">
            {/* Metric Labels Header */}
            <div className="col-span-1 p-6 flex items-end">
              <span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">
                Evaluation Metrics
              </span>
            </div>

            {/* Candidates Headers */}
            {compareList.map((candidate) => (
              <div
                key={candidate.id}
                className="col-span-1 p-6 flex flex-col items-center text-center border-l border-white/5 bg-white/[0.01]"
              >
                <div className="relative mb-4">
                  <img
                    className="w-20 h-20 rounded-full object-cover border-2 border-primary shadow-[0_0_15px_rgba(192,193,255,0.3)]"
                    src={candidate.avatar}
                    alt={candidate.name}
                  />
                  {candidate.ranking === 'Top 1%' && (
                    <div className="absolute -bottom-2 -right-2 bg-surface-container-highest border border-white/20 rounded-full p-1 shadow-lg">
                      <span className="material-symbols-outlined text-[14px] text-tertiary-fixed font-bold">star</span>
                    </div>
                  )}
                </div>
                <h3 className="font-headline-md text-lg font-bold text-on-surface leading-tight mb-1">
                  {candidate.name}
                </h3>
                <p className="font-label-sm text-label-sm text-on-surface-variant/75 mb-4">
                  {candidate.prevRole}
                </p>
                <button
                  onClick={() => navigate(`/profile/${candidate.id}`)}
                  className="w-full py-2 rounded-lg bg-primary text-on-primary font-label-md text-label-md hover:bg-primary-fixed transition-colors shadow-[inset_0_1px_0_rgba(255,255,255,0.2)] cursor-pointer active:scale-95"
                >
                  View Full Profile
                </button>
              </div>
            ))}
          </div>

          {/* Matrix Rows */}
          {/* Row 1: AI Match Score */}
          <div className="grid grid-cols-4 border-b border-white/5 hover:bg-white/[0.01] transition-colors">
            <div className="col-span-1 p-6 font-bold text-sm text-on-surface flex items-center">
              AI Match Score
            </div>
            {compareList.map((candidate) => (
              <div
                key={candidate.id}
                className="col-span-1 p-6 border-l border-white/5 flex flex-col items-center justify-center bg-white/[0.01]"
              >
                <span className={`px-4 py-1.5 rounded-full font-black font-headline text-lg ${getScoreColorClass(candidate.score)}`}>
                  {candidate.score}%
                </span>
                <span className="text-[10px] uppercase font-bold text-on-surface-variant/60 tracking-wider mt-1.5">
                  {candidate.matchType}
                </span>
              </div>
            ))}
          </div>

          {/* Row 2: Work Experience */}
          <div className="grid grid-cols-4 border-b border-white/5 hover:bg-white/[0.01] transition-colors">
            <div className="col-span-1 p-6 font-bold text-sm text-on-surface flex items-center">
              Work Experience
            </div>
            {compareList.map((candidate) => (
              <div
                key={candidate.id}
                className="col-span-1 p-6 border-l border-white/5 flex items-center justify-center text-center text-sm font-medium bg-white/[0.01]"
              >
                {candidate.experience}
              </div>
            ))}
          </div>

          {/* Row 3: Educational Background */}
          <div className="grid grid-cols-4 border-b border-white/5 hover:bg-white/[0.01] transition-colors">
            <div className="col-span-1 p-6 font-bold text-sm text-on-surface flex items-center">
              Education
            </div>
            {compareList.map((candidate) => (
              <div
                key={candidate.id}
                className="col-span-1 p-6 border-l border-white/5 flex items-center justify-center text-center text-xs text-on-surface-variant font-medium bg-white/[0.01]"
              >
                {candidate.education}
              </div>
            ))}
          </div>

          {/* Row 4: Core Skills Matches */}
          <div className="grid grid-cols-4 border-b border-white/5 hover:bg-white/[0.01] transition-colors">
            <div className="col-span-1 p-6 font-bold text-sm text-on-surface flex items-center">
              Matching Core Skills
            </div>
            {compareList.map((candidate) => {
              const matchedSkills = Object.entries(candidate.skills)
                .filter(([_, status]) => status === 'match')
                .map(([skill]) => skill);

              return (
                <div
                  key={candidate.id}
                  className="col-span-1 p-6 border-l border-white/5 bg-white/[0.01] flex flex-wrap gap-2 justify-center items-center"
                >
                  {matchedSkills.map((skill) => (
                    <span key={skill} className="px-2 py-0.5 rounded-full font-label-sm text-label-sm font-semibold tag-green">
                      {skill}
                    </span>
                  ))}
                </div>
              );
            })}
          </div>

          {/* Row 5: Identified Skill Gaps */}
          <div className="grid grid-cols-4 hover:bg-white/[0.01] transition-colors">
            <div className="col-span-1 p-6 font-bold text-sm text-on-surface flex items-center">
              Identified Gaps
            </div>
            {compareList.map((candidate) => {
              const gapSkills = Object.entries(candidate.skills)
                .filter(([_, status]) => status === 'gap')
                .map(([skill]) => skill);

              return (
                <div
                  key={candidate.id}
                  className="col-span-1 p-6 border-l border-white/5 bg-white/[0.01] flex flex-wrap gap-2 justify-center items-center"
                >
                  {gapSkills.length > 0 ? (
                    gapSkills.map((skill) => (
                      <span key={skill} className="px-2 py-0.5 rounded-full font-label-sm text-label-sm font-semibold tag-red">
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-on-surface-variant italic">No gaps identified</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidateComparison;
