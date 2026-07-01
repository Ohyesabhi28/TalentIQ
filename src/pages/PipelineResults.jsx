import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import GlassCard from '../components/common/GlassCard';
import AICopilotCard from '../components/common/AICopilotCard';
import mockData from '../data/mockData.json';

const PipelineResults = ({ candidates, allCandidatesCount }) => {
  const navigate = useNavigate();
  const [selectedCandidates, setSelectedCandidates] = useState([]);

  const handleToggleCompare = (id) => {
    setSelectedCandidates((prev) =>
      prev.includes(id) ? prev.filter((cId) => cId !== id) : [...prev, id]
    );
  };

  const getScoreColorClass = (score) => {
    if (score >= 90) return 'tag-green text-glow';
    if (score >= 80) return 'text-[#34d399] bg-[#10b981]/15 border border-[#10b981]/20';
    return 'text-[#f87171] bg-[#ef4444]/15 border border-[#ef4444]/20';
  };

  // Find top fit candidate dynamically from current active candidates
  const topFitCandidate = candidates.length > 0 
    ? [...candidates].sort((a, b) => b.score - a.score)[0] 
    : null;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-primary font-bold tracking-widest text-[10px] uppercase block mb-1">
            Sourcing Pipeline
          </span>
          <h1 className="text-headline-lg font-bold text-on-surface">
            {mockData.jobDescription.title}
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/report')}
            className="btn-ghost px-5 py-2.5 rounded-lg font-label-md text-label-md cursor-pointer hover:border-white/40 flex items-center gap-2 active:scale-95 transition-transform"
          >
            <span className="material-symbols-outlined text-[18px]">assignment</span>
            Hiring Report
          </button>
          {selectedCandidates.length >= 2 && (
            <button
              onClick={() => navigate('/comparison')}
              className="btn-primary px-5 py-2.5 rounded-lg font-label-md text-label-md cursor-pointer flex items-center gap-2 active:scale-95 transition-transform glow-btn"
            >
              <span className="material-symbols-outlined text-[18px]">compare_arrows</span>
              Compare Selected ({selectedCandidates.length})
            </button>
          )}
        </div>
      </header>

      {/* Overview Stat Widgets */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlassCard className="p-5 flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-primary-container/10 flex items-center justify-center border border-primary-container/20">
            <span className="material-symbols-outlined text-primary text-2xl">folder_zip</span>
          </div>
          <div>
            <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Analyzed Resumes</p>
            <h3 className="text-2xl font-bold text-white mt-0.5">{allCandidatesCount} Profiles</h3>
          </div>
        </GlassCard>

        <GlassCard className="p-5 flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-tertiary-container/10 flex items-center justify-center border border-tertiary-container/20">
            <span className="material-symbols-outlined text-tertiary text-2xl">verified</span>
          </div>
          <div>
            <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Top Semantic Fit</p>
            <h3 className="text-2xl font-bold text-white mt-0.5">
              {topFitCandidate ? `${topFitCandidate.name} (${topFitCandidate.score}%)` : 'None'}
            </h3>
          </div>
        </GlassCard>

        <GlassCard className="p-5 flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-green-500/10 flex items-center justify-center border border-green-500/20">
            <span className="material-symbols-outlined text-green-400 text-2xl">bar_chart</span>
          </div>
          <div>
            <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Critical Skills Match</p>
            <h3 className="text-2xl font-bold text-white mt-0.5">85% Avg</h3>
          </div>
        </GlassCard>
      </section>

      {/* AI Copilot Advisor Insight */}
      <AICopilotCard>
        <div className="flex items-start gap-4">
          <div className="h-8 w-8 rounded-full bg-primary-container/10 border border-primary-container/20 flex items-center justify-center shrink-0 text-primary">
            <span className="material-symbols-outlined text-[18px]">smart_toy</span>
          </div>
          <div className="space-y-1">
            <h4 className="font-bold text-white text-body-md">AI Recruiter Summary</h4>
            <p className="text-on-surface-variant text-sm leading-relaxed">
              {mockData.summaryReport.recruiterSummary}
            </p>
          </div>
        </div>
      </AICopilotCard>

      {/* Pipeline Grid List */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-headline-md text-headline-md text-on-surface">Candidate Rankings</h3>
          <span className="text-label-sm text-on-surface-variant font-medium">Sorted by AI Match Score</span>
        </div>

        <div className="space-y-4">
          {candidates.map((candidate) => {
            const isSelected = selectedCandidates.includes(candidate.id);
            // Count matches and gaps
            const matchesCount = Object.values(candidate.skills).filter((s) => s === 'match').length;
            const totalCount = Object.keys(candidate.skills).length;

            return (
              <GlassCard
                key={candidate.id}
                className={`p-6 border transition-all duration-300 hover:border-white/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 ${
                  isSelected ? 'border-primary/30 bg-primary/5' : ''
                }`}
              >
                {/* Left Profile Info */}
                <div className="flex items-center gap-4 shrink-0">
                  <div className="relative">
                    <img
                      className="w-14 h-14 rounded-full object-cover border border-white/10"
                      src={candidate.avatar}
                      alt={candidate.name}
                    />
                    <div className="absolute -bottom-1 -right-1 h-6 w-6 rounded-full bg-surface-container-highest border border-white/20 flex items-center justify-center font-bold text-[9px] text-white">
                      {candidate.ranking === 'Top 1%' ? '★' : ''}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-headline-sm text-lg font-bold text-on-surface">{candidate.name}</h4>
                    <p className="text-on-surface-variant text-xs mt-0.5">{candidate.prevRole}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <p className="text-on-surface-variant text-[11px] font-medium uppercase tracking-widest">
                        {candidate.experience} Experience
                      </p>
                      {candidate.fileName && (
                        <span className="text-[10px] text-primary bg-primary/5 px-2 py-0.5 rounded border border-primary/10">
                          {candidate.fileName}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Center: Score Progress & Info */}
                <div className="flex-1 w-full flex flex-col md:flex-row items-start md:items-center gap-6">
                  {/* Match Score */}
                  <div className="flex items-center gap-3 shrink-0">
                    <div className={`px-3 py-1.5 rounded-full font-bold text-sm ${getScoreColorClass(candidate.score)}`}>
                      {candidate.score}% Match
                    </div>
                    <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                      {candidate.matchType}
                    </span>
                  </div>

                  {/* Skills summary progress */}
                  <div className="flex-1 w-full space-y-1.5">
                    <div className="flex justify-between font-label-sm text-label-sm text-on-surface-variant">
                      <span>Skills Match</span>
                      <span>{matchesCount}/{totalCount} Skills</span>
                    </div>
                    <div className="w-full h-2 bg-surface-container-low rounded-full overflow-hidden">
                      <div
                        className="h-full chart-bar-primary rounded-full"
                        style={{ width: `${(matchesCount / totalCount) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Right Actions */}
                <div className="flex items-center justify-end gap-4 shrink-0 w-full md:w-auto pt-4 md:pt-0 border-t border-white/5 md:border-none">
                  {/* Compare Checkbox */}
                  <label className="flex items-center gap-2 font-label-sm text-label-sm text-on-surface-variant cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => handleToggleCompare(candidate.id)}
                      className="rounded border-white/10 text-primary focus:ring-0 focus:ring-offset-0 bg-transparent h-4 w-4"
                    />
                    Compare
                  </label>

                  {/* View Details */}
                  <button
                    onClick={() => navigate(`/profile/${candidate.id}`)}
                    className="primary-btn px-4 py-2 rounded-lg font-label-md text-label-md cursor-pointer active:scale-95"
                  >
                    View Details
                  </button>
                </div>
              </GlassCard>
            );
          })}
        </div>
      </section>
    </div>
  );
};

export default PipelineResults;
