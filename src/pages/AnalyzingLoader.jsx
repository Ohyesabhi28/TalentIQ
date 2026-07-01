import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import AnalyzingSVG from '../components/common/AnalyzingSVG';
import GlassCard from '../components/common/GlassCard';
import { getJobStatus } from '../utils/api';

const AnalyzingLoader = ({ activeJobId, setActiveJobId }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState(null);

  // Extract jobId from URL search params or activeJobId state
  const params = new URLSearchParams(location.search);
  const jobId = params.get('jobId') || activeJobId;

  const [stages, setStages] = useState([
    { id: 1, label: 'Extracting semantic layers from job description...', status: 'pending' },
    { id: 2, label: 'Parsing candidate resumes...', status: 'pending' },
    { id: 3, label: 'Performing cross-signal skill gap matching...', status: 'pending' },
    { id: 4, label: 'Generating recruiter insights...', status: 'pending' },
  ]);

  const [eta, setEta] = useState(32);

  useEffect(() => {
    if (!jobId) {
      setError("No active job session found. Please start a new sourcing run.");
      return;
    }

    let intervalId;

    const pollStatus = async () => {
      try {
        const job = await getJobStatus(jobId);
        
        // Update stages
        if (job.progress_stages && job.progress_stages.length > 0) {
          setStages(job.progress_stages.map(s => ({
            id: s.id,
            label: s.label,
            status: s.status
          })));
        }

        // ETA mapping
        if (job.status === 'completed') {
          setEta(0);
          clearInterval(intervalId);
          setTimeout(() => {
            navigate('/results');
          }, 1000);
        } else if (job.status === 'failed') {
          clearInterval(intervalId);
          setError(job.error_message || "An error occurred during background analysis pipeline execution.");
        } else {
          // Approximate countdown
          setEta(prev => Math.max(prev - 2, 4));
        }

      } catch (err) {
        console.warn("Polling error:", err);
      }
    };

    // Run immediately and then poll every 2s
    pollStatus();
    intervalId = setInterval(pollStatus, 2000);

    return () => clearInterval(intervalId);
  }, [jobId, navigate]);

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
            {error ? 'Analysis Halted' : 'Processing Data...'}
          </div>
        </div>
      </div>

      {/* Error State */}
      {error ? (
        <GlassCard className="w-full p-6 md:p-8 space-y-4 border border-red-500/20 text-center">
          <div className="h-12 w-12 rounded-full bg-red-500/10 flex items-center justify-center mx-auto text-red-400">
            <span className="material-symbols-outlined">error</span>
          </div>
          <h2 className="text-xl font-bold text-white">Pipeline Execution Error</h2>
          <p className="text-on-surface-variant text-sm max-w-lg mx-auto">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="primary-btn px-6 py-2.5 rounded-lg text-sm font-semibold cursor-pointer active:scale-95 inline-flex items-center gap-2"
          >
            <span className="material-symbols-outlined">restart_alt</span>
            Start New Sourcing
          </button>
        </GlassCard>
      ) : (
        /* Pipeline Status Container */
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
                ~{eta}<span className="font-body-lg text-body-lg text-on-surface-variant font-normal">s</span>
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
                    <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center border border-white/10 text-on-surface-variant/40">
                      <span className="material-symbols-outlined text-[18px]">hourglass_empty</span>
                    </div>
                  )}
                </div>
                <div>
                  <p className={`text-sm font-semibold ${
                    stage.status === 'loading' ? 'text-primary' : 'text-on-surface'
                  }`}>
                    {stage.label}
                  </p>
                  <p className="text-[10px] text-on-surface-variant capitalize mt-0.5">{stage.status}</p>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      )}
    </div>
  );
};

export default AnalyzingLoader;
