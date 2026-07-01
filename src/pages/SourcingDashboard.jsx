import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import GlassCard from '../components/common/GlassCard';
import { uploadFile, createAnalysisJob } from '../utils/api';

const SourcingDashboard = ({ jdFile, setJdFile, resumes, setResumes, activeJobId, setActiveJobId }) => {
  const navigate = useNavigate();
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const handleJdDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setJdFile(file);
    }
  };

  const handleResumesDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      const newFiles = Array.from(e.dataTransfer.files);
      setResumes((prev) => [...prev, ...newFiles]);
    }
  };

  const handleFileBrowse = (type) => {
    const input = document.createElement('input');
    input.type = 'file';
    if (type === 'jd') {
      input.accept = '.pdf,.docx,.txt';
      input.onchange = (e) => {
        if (e.target.files && e.target.files[0]) {
          const file = e.target.files[0];
          setJdFile(file);
        }
      };
    } else {
      input.multiple = true;
      input.accept = '.pdf,.docx,.txt';
      input.onchange = (e) => {
        if (e.target.files) {
          const newFiles = Array.from(e.target.files);
          setResumes((prev) => [...prev, ...newFiles]);
        }
      };
    }
    input.click();
  };

  const handleRemoveResume = (index) => {
    setResumes((prev) => prev.filter((_, i) => i !== index));
  };

  const handleAnalyze = async () => {
    if (!jdFile || resumes.length === 0) return;
    
    setAnalyzing(true);
    setError(null);
    
    try {
      // 1. Upload Job Description
      const jdResult = await uploadFile(jdFile, "job_description");
      const jdFileId = jdResult.id;
      
      // 2. Upload Resumes in parallel
      const resumeUploadPromises = resumes.map(file => uploadFile(file, "resume"));
      const resumeResults = await Promise.all(resumeUploadPromises);
      const resumeFileIds = resumeResults.map(r => r.id);
      
      // 3. Create Analysis Job
      const job = await createAnalysisJob(jdFileId, resumeFileIds);
      
      // 4. Update state and navigate
      setActiveJobId(job.id);
      navigate(`/analyzing?jobId=${job.id}`);
      
    } catch (err) {
      console.error("Analysis pipeline start failed:", err);
      setError(err.message || "Failed to initiate candidate sourcing analysis. Please check that the backend service is running.");
    } finally {
      setAnalyzing(false);
    }
  };

  const totalSize = (resumes.reduce((acc, f) => acc + f.size, 0) / (1024 * 1024)).toFixed(2);

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-8">
        <h1 className="text-display-lg font-bold text-on-surface mb-4 tracking-tighter leading-tight">
          Find the Best Talent in Seconds
        </h1>
        <p className="text-body-lg text-on-surface-variant max-w-2xl mx-auto font-light leading-relaxed">
          Upload a job description and a batch of resumes. Our Enterprise AI will instantly analyze, score, and rank candidates based on semantic fit and skill gap analysis.
        </p>
      </section>

      {/* Error Message */}
      {error && (
        <div className="bg-red-950/40 border border-red-500/20 text-red-200 px-6 py-4 rounded-xl text-sm flex items-center gap-3">
          <span className="material-symbols-outlined text-red-400">error</span>
          <span>{error}</span>
        </div>
      )}

      {/* Upload Grid */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-gutter">
        {/* Job Description Upload */}
        <GlassCard className="p-6 flex flex-col min-h-[350px]">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-headline-md text-headline-md text-on-surface">Target Role</h2>
            <span className="text-primary-fixed bg-primary/10 px-3 py-1 rounded-full font-label-sm text-label-sm border border-primary/20">
              Step 1
            </span>
          </div>

          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleJdDrop}
            className="upload-area flex-grow rounded-xl flex flex-col items-center justify-center p-8 text-center cursor-pointer group"
            onClick={() => handleFileBrowse('jd')}
          >
            <div className="h-16 w-16 rounded-2xl bg-white/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 border border-white/10">
              <span className="material-symbols-outlined text-4xl text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
                description
              </span>
            </div>
            {jdFile ? (
              <div>
                <p className="font-label-md text-label-md text-primary font-semibold mb-1">{jdFile.name}</p>
                <p className="font-label-sm text-label-sm text-on-surface-variant">
                  {(jdFile.size / 1024).toFixed(1)} KB — Ready
                </p>
              </div>
            ) : (
              <div>
                <p className="font-label-md text-label-md text-on-surface font-semibold mb-1">
                  Drag &amp; drop Job Description here
                </p>
                <p className="font-label-sm text-label-sm text-on-surface-variant font-light">
                  or click to browse local files (.pdf, .docx, .txt)
                </p>
              </div>
            )}
          </div>
        </GlassCard>

        {/* Resumes Batch Upload */}
        <GlassCard className="p-6 flex flex-col min-h-[350px]">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-headline-md text-headline-md text-on-surface">Candidate Pool</h2>
            <span className="text-primary-fixed bg-primary/10 px-3 py-1 rounded-full font-label-sm text-label-sm border border-primary/20">
              Step 2
            </span>
          </div>

          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleResumesDrop}
            className="upload-area flex-grow rounded-xl flex flex-col items-center justify-center p-8 text-center cursor-pointer group"
            onClick={() => handleFileBrowse('resumes')}
          >
            <div className="h-16 w-16 rounded-2xl bg-white/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 border border-white/10">
              <span className="material-symbols-outlined text-4xl text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
                upload_file
              </span>
            </div>
            <div>
              <p className="font-label-md text-label-md text-on-surface font-semibold mb-1">
                Drag &amp; drop resumes batch here
              </p>
              <p className="font-label-sm text-label-sm text-on-surface-variant font-light">
                or click to browse multiple resumes (.pdf, .docx, .txt)
              </p>
            </div>
          </div>
        </GlassCard>
      </section>

      {/* Upload Progress / Batch List */}
      {resumes.length > 0 && (
        <GlassCard className="p-6 space-y-4">
          <div className="flex justify-between items-center border-b border-white/5 pb-4">
            <div>
              <h3 className="font-headline-sm text-lg font-bold text-on-surface">Selected Resumes</h3>
              <p className="text-xs text-on-surface-variant mt-0.5">{resumes.length} files selected ({totalSize} MB)</p>
            </div>
            <button
              onClick={() => setResumes([])}
              className="text-label-sm text-red-400 hover:text-red-300 font-semibold cursor-pointer"
            >
              Clear Batch
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[250px] overflow-y-auto pr-2">
            {resumes.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 rounded-lg border border-white/5 bg-white/5"
              >
                <div className="flex items-center gap-2.5 overflow-hidden">
                  <span className="material-symbols-outlined text-primary shrink-0">insert_drive_file</span>
                  <div className="overflow-hidden">
                    <p className="text-xs font-semibold text-white truncate">{file.name}</p>
                    <p className="text-[10px] text-on-surface-variant mt-0.5">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); handleRemoveResume(index); }}
                  className="text-on-surface-variant hover:text-white shrink-0 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[16px]">close</span>
                </button>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* Start Button */}
      {jdFile && resumes.length > 0 && (
        <div className="flex justify-center pt-4">
          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="px-10 py-4 bg-primary text-on-primary rounded-xl font-label-lg text-label-lg shadow-[0_0_30px_rgba(192,193,255,0.3)] hover:shadow-[0_0_40px_rgba(192,193,255,0.5)] transition-all glow-btn tracking-wide font-black cursor-pointer active:scale-95 flex items-center gap-3"
          >
            {analyzing ? (
              <>
                <span className="material-symbols-outlined animate-spin">sync</span>
                Uploading &amp; Analyzing...
              </>
            ) : (
              <>
                <span className="material-symbols-outlined">analytics</span>
                Start Candidate Sourcing
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default SourcingDashboard;
