import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import GlassCard from '../components/common/GlassCard';
import AICopilotCard from '../components/common/AICopilotCard';
import mockData from '../data/mockData.json';

const CandidateProfile = ({ candidates }) => {
  const { id } = useParams();
  const navigate = useNavigate();

  // Find candidate from props candidates array, fallback to mockData if not found
  const candidate = (candidates && candidates.find((c) => c.id === id)) || 
                    mockData.candidates.find((c) => c.id === id) || 
                    mockData.candidates[0];

  const getScoreColor = (score) => {
    if (score >= 90) return '#c0c1ff'; // primary
    if (score >= 80) return '#4ae176'; // secondary
    return '#ffb4ab'; // error
  };

  // SVG dash calculation for circular score chart
  const radius = 40;
  const strokeWidth = 8;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (candidate.score / 100) * circumference;

  return (
    <div className="space-y-8">
      {/* Back Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <Link
            to="/results"
            className="inline-flex items-center text-primary font-label-sm text-label-sm hover:underline mb-2"
          >
            <span className="material-symbols-outlined text-[16px] mr-1">arrow_back</span>
            Back to pipeline results
          </Link>
          <h1 className="text-headline-lg font-bold text-white tracking-tight">Candidate Sourcing Dossier</h1>
        </div>
        <button
          onClick={() => navigate('/comparison')}
          className="btn-ghost px-5 py-2.5 rounded-lg font-label-md text-label-md cursor-pointer hover:border-white/40 flex items-center gap-2 active:scale-95 transition-transform"
        >
          <span className="material-symbols-outlined text-[18px]">compare_arrows</span>
          Candidate Comparison
        </button>
      </header>

      {/* Main Profile Info Card */}
      <GlassCard className="p-6 md:p-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary-container/5 blur-[100px] pointer-events-none"></div>

        {/* User Card Left */}
        <div className="flex items-center gap-6">
          <img
            className="w-24 h-24 rounded-full object-cover border-2 border-primary shadow-[0_0_20px_rgba(192,193,255,0.2)]"
            src={candidate.avatar}
            alt={candidate.name}
          />
          <div className="space-y-1.5">
            <div className="flex items-center gap-3">
              <h2 className="text-headline-md font-bold text-white tracking-tight leading-none">
                {candidate.name}
              </h2>
              <span className="bg-primary-container/20 text-primary-fixed border border-primary/20 text-[10px] px-2 py-0.5 rounded-md font-black uppercase tracking-wider">
                {candidate.ranking}
              </span>
            </div>
            <p className="font-label-md text-label-md text-on-surface-variant">{candidate.prevRole}</p>
            <div className="flex flex-col gap-1">
              <p className="font-label-sm text-label-sm text-on-surface-variant/75 flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px] text-primary">school</span>
                {candidate.education}
              </p>
              {candidate.fileName && (
                <p className="font-label-sm text-label-sm text-primary flex items-center gap-2 mt-0.5">
                  <span className="material-symbols-outlined text-[16px]">insert_drive_file</span>
                  Source Resume: {candidate.fileName}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Circular Chart Score Right */}
        <div className="flex items-center gap-6 shrink-0 bg-white/5 border border-white/5 p-5 rounded-2xl min-w-[220px]">
          <div className="relative w-20 h-20">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                className="text-white/10"
                strokeWidth={strokeWidth}
                stroke="currentColor"
                fill="transparent"
                r={radius}
                cx="40"
                cy="40"
              />
              <circle
                stroke={getScoreColor(candidate.score)}
                strokeWidth={strokeWidth}
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                r={radius}
                cx="40"
                cy="40"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center font-headline font-bold text-xl text-white">
              {candidate.score}%
            </div>
          </div>
          <div>
            <div className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">
              Match Level
            </div>
            <div className="text-lg font-bold text-white leading-none">{candidate.matchType}</div>
            <div className="text-xs text-primary mt-1 font-medium">{candidate.experience} experience</div>
          </div>
        </div>
      </GlassCard>

      {/* AI Explanation Insight */}
      <AICopilotCard>
        <div className="flex items-start gap-4">
          <div className="h-8 w-8 rounded-full bg-primary-container/10 border border-primary-container/20 flex items-center justify-center shrink-0 text-primary">
            <span className="material-symbols-outlined text-[18px]">smart_toy</span>
          </div>
          <div className="space-y-1">
            <h4 className="font-bold text-white text-body-md">Recruiter Copilot Explanation</h4>
            <p className="text-on-surface-variant text-sm leading-relaxed">{candidate.aiReasoning}</p>
          </div>
        </div>
      </AICopilotCard>

      {/* Bottom Grid Detail Block */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
        {/* Left Column: Work Experience Timeline */}
        <GlassCard className="p-6 md:p-8 lg:col-span-7 space-y-6">
          <h3 className="font-headline-md text-headline-md text-white">Work History</h3>
          <div className="relative border-l border-white/10 pl-6 ml-2 space-y-8">
            {candidate.experienceDetail.map((exp, index) => (
              <div key={index} className="relative space-y-2">
                {/* Marker Dot */}
                <div className="absolute -left-[31px] top-1.5 w-3.5 h-3.5 rounded-full bg-primary border-4 border-surface shadow-[0_0_10px_rgba(192,193,255,0.4)]"></div>
                <div className="flex flex-wrap justify-between items-baseline gap-2">
                  <h4 className="font-bold text-white text-lg">{exp.role}</h4>
                  <span className="font-label-sm text-label-sm text-primary font-medium">{exp.period}</span>
                </div>
                <p className="font-label-md text-label-md text-on-surface-variant font-semibold">
                  {exp.company}
                </p>
                <ul className="list-disc pl-5 space-y-1.5 text-sm text-on-surface-variant opacity-90 leading-relaxed font-light">
                  {exp.bullets.map((bullet, i) => (
                    <li key={i}>{bullet}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Right Column: Skills Checklist */}
        <GlassCard className="p-6 md:p-8 lg:col-span-5 space-y-6 flex flex-col">
          <h3 className="font-headline-md text-headline-md text-white">Technical Skills Gap</h3>
          <div className="space-y-3 flex-grow">
            {Object.entries(candidate.skills).map(([skill, status]) => {
              const isMatch = status === 'match';
              return (
                <div
                  key={skill}
                  className={`flex items-center justify-between p-3 rounded-lg border ${
                    isMatch
                      ? 'bg-[#10b981]/5 border-[#10b981]/10'
                      : 'bg-[#ef4444]/5 border-[#ef4444]/10'
                  }`}
                >
                  <span className="font-semibold text-sm text-on-surface">{skill}</span>
                  <span className={`px-2.5 py-0.5 rounded-full font-label-sm text-label-sm font-bold uppercase ${
                    isMatch ? 'tag-green' : 'tag-red'
                  }`}>
                    {isMatch ? 'Match' : 'Gap'}
                  </span>
                </div>
              );
            })}
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

export default CandidateProfile;
