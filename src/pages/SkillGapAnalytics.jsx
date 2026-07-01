import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import GlassCard from '../components/common/GlassCard';
import AICopilotCard from '../components/common/AICopilotCard';
import mockData from '../data/mockData.json';

const SkillGapAnalytics = ({ activeJobId }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      const jobId = activeJobId || "00000000-0000-0000-0000-000000000000";
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:8000/v1/analysis/jobs/${jobId}/analytics`);
        if (response.ok) {
          const resJson = await response.json();
          if (resJson && resJson.data) {
            setAnalytics(resJson.data);
          }
        }
      } catch (err) {
        console.warn("Could not load backend analytics, falling back to mock data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, [activeJobId]);

  const skillDistribution = analytics 
    ? [
        ...analytics.skill_gap.top_matching_skills.map(s => ({ ...s, isMatch: true })),
        ...analytics.skill_gap.top_missing_skills.map(s => ({ ...s, isMatch: false }))
      ].slice(0, 8).map(s => ({
        skillName: s.skill_name,
        matchCount: s.match_count,
        gapCount: s.gap_count
      }))
    : mockData.roleSkillGap.distribution;

  const insights = analytics
    ? [
        {
          category: "Most Requested Skills",
          message: `The primary required skills for this role are: ${analytics.skill_gap.most_requested_skills.join(', ')}.`
        },
        {
          category: "Technology Profile",
          message: `Most common candidate technologies include: ${analytics.skill_gap.most_common_technologies.slice(0, 5).join(', ')}.`
        },
        {
          category: "Certifications",
          message: `The most common certifications observed are: ${analytics.skill_gap.most_common_certifications.join(', ') || 'None'}.`
        }
      ]
    : mockData.roleSkillGap.actionableInsights;

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
          <h2 className="text-headline-lg font-bold text-on-surface tracking-tight">Role-level Skill Distribution</h2>
        </div>
      </header>

      {/* Grid containing Charts & Action Items */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
        {/* Left Column: Horizontal Bar Charts */}
        <GlassCard className="p-6 md:p-8 lg:col-span-8 space-y-6">
          <h3 className="font-headline-md text-headline-md text-white">Sourcing Breakdown</h3>
          <div className="space-y-6">
            {skillDistribution.map((skill, index) => {
              const total = skill.matchCount + skill.gapCount;
              const matchPercent = total > 0 ? (skill.matchCount / total) * 100 : 0;
              const gapPercent = total > 0 ? (skill.gapCount / total) * 100 : 0;

              return (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between font-semibold text-sm text-on-surface">
                    <span>{skill.skillName}</span>
                    <span className="text-xs text-on-surface-variant font-normal">
                      {skill.matchCount} Matches / {skill.gapCount} Gaps
                    </span>
                  </div>

                  {/* Horizontal Bar */}
                  <div className="w-full h-4 bg-surface-container-low rounded-full overflow-hidden flex">
                    {/* Match Bar */}
                    <div
                      className="h-full chart-bar-primary animated-bar"
                      style={{ width: `${matchPercent}%` }}
                    ></div>
                    {/* Gap Bar */}
                    <div
                      className="h-full bg-error-container animate-pulse-border"
                      style={{ width: `${gapPercent}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </GlassCard>

        {/* Right Column: Sourcing level Insights & Recommendations */}
        <GlassCard className="p-6 md:p-8 lg:col-span-4 flex flex-col justify-between">
          <div className="space-y-6">
            <h3 className="font-headline-md text-headline-md text-white">Actionable Insights</h3>
            <div className="space-y-4">
              {insights.map((insight, index) => (
                <div
                  key={index}
                  className="insight-glow p-4 bg-white/5 border border-white/5 rounded-xl space-y-2"
                >
                  <div className="font-bold text-xs uppercase tracking-wider text-primary">
                    {insight.category}
                  </div>
                  <p className="text-sm text-on-surface-variant leading-relaxed font-light">
                    {insight.message}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-8 border-t border-white/10 mt-8 flex flex-col gap-3">
            <div className="text-xs text-on-surface-variant font-medium">
              Want custom training paths generated for candidates?
            </div>
            <button className="primary-btn w-full py-2.5 rounded-lg font-label-md text-label-md cursor-pointer active:scale-95 transition-transform">
              Generate AI Training Plan
            </button>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

export default SkillGapAnalytics;
