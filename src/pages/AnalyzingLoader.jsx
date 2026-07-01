import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AnalyzingSVG from '../components/common/AnalyzingSVG';
import GlassCard from '../components/common/GlassCard';

const AnalyzingLoader = () => {
  const navigate = useNavigate();
  const [stages, setStages] = useState([
    { id: 1, text: 'Extracting semantic layers from job description...', status: 'done' },
    { id: 2, text: 'Parsing candidate resumes...', status: 'done' },
    { id: 3, text: 'Performing cross-signal skill gap matching...', status: 'loading' },
    { id: 4, text: 'Generating recruiter insights...', status: 'pending' },
  ]);

  useEffect(() => {
    // Stage 3 completes after 1.5 seconds, then Stage 4 starts
    const timer1 = setTimeout(() => {
      setStages((prev) =>
        prev.map((stage) => {
          if (stage.id === 3) return { ...stage, status: 'done' };
          if (stage.id === 4) return { ...stage, status: 'loading' };
          return stage;
        })
      );
    }, 1500);

    // Stage 4 completes and redirects after 3 seconds
    const timer2 = setTimeout(() => {
      setStages((prev) =>
        prev.map((stage) => {
          if (stage.id === 4) return { ...stage, status: 'done' };
          return stage;
        })
      );
      navigate('/results');
    }, 3000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [navigate]);

  return (
    <div className="max-w-4xl mx-auto flex flex-col items-center py-8">
      {/* Centerpiece SVG Card */}
      <div className="w-full h-64 md:h-96 relative mb-12 flex items-center justify-center">
        <div className="absolute inset-0 flex items-center justify-center opacity-20">
          <div className="w-64 h-64 rounded-full bg-primary-container blur-3xl"></div>
        </div>
        <div className="relative w-full h-full z-10 glass-card rounded-2xl overflow-hidden flex items-center justify-center border-l-4 border-l-primary shadow-[0_0_40px_rgba(192,193,255,0.1)]">
          <AnalyzingSVG />
          <div className="absolute bottom-4 right-4 bg-surface-container/80 backdrop-blur-md px-4 py-2 rounded-full border border-white/10 font-label-sm text-label-sm flex items-center gap-2 text-primary">
            <span className="material-symbols-outlined text-[16px] animate-spin-slow">sync</span>
            Processing Data...
          </div>
        </div>
      </div>

      {/* Pipeline Status Container */}
      <GlassCard className="w-full rounded-xl p-6 md:p-8 flex flex-col md:flex-row gap-8 items-start">
        {/* Left Status Summary */}
        <div className="w-full md:w-1/3 flex flex-col">
          <h1 className="font-display-lg text-headline-lg md:text-[40px] text-white mb-2 leading-tight font-bold">
            AI Agent<br />Active
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant mb-6">
            Evaluating candidate profiles against job requirements.
          </p>
          <div className="mt-auto pt-6 border-t border-white/10">
            <div className="font-label-sm text-label-sm text-primary mb-1 uppercase tracking-wider">
              Estimated Time Remaining
            </div>
            <div className="font-headline-lg text-headline-lg text-white flex items-baseline gap-2 font-bold">
              ~32<span className="font-body-lg text-body-lg text-on-surface-variant font-normal">s</span>
            </div>
          </div>
        </div>

        {/* Right Stages List */}
        <div className="w-full md:w-2/3 flex flex-col gap-3">
          {stages.map((stage) => (
            <div
              key={stage.id}
              className={`flex items-center gap-4 p-3.5 rounded-lg border transition-all duration-300 ${
                stage.status === 'done'
                  ? 'bg-white/5 border-white/5 opacity-80'
                  : stage.status === 'loading'
                  ? 'bg-primary/5 border-primary/20 animate-pulse'
                  : 'bg-transparent border-white/5 opacity-40'
              }`}
            >
              <div className="shrink-0 flex items-center justify-center">
                {stage.status === 'done' ? (
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center border border-primary/50 text-primary">
                    <span className="material-symbols-outlined text-[18px]">check</span>
                  </div>
                ) : stage.status === 'loading' ? (
                  <div className="w-8 h-8 rounded-full bg-primary-container/20 flex items-center justify-center border border-primary-container text-primary-container animate-spin">
                    <span className="material-symbols-outlined text-[18px]">sync</span>
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center border border-white/10 text-on-surface-variant">
                    <span className="material-symbols-outlined text-[18px]">hourglass_empty</span>
                  </div>
                )}
              </div>
              <p className="font-label-md text-label-md text-on-surface leading-tight">
                {stage.text}
              </p>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
};

export default AnalyzingLoader;
