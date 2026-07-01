import React from 'react';
import { useNavigate } from 'react-router-dom';
import GlassCard from '../components/common/GlassCard';

const SourcingDashboard = ({ jdFile, setJdFile, resumes, setResumes }) => {
  const navigate = useNavigate();

  const handleJdDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setJdFile({ name: file.name, size: file.size });
    }
  };

  const handleResumesDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      const newFiles = Array.from(e.dataTransfer.files).map((f) => ({
        name: f.name,
        size: f.size,
      }));
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
          setJdFile({ name: file.name, size: file.size });
        }
      };
    } else {
      input.multiple = true;
      input.accept = '.pdf,.docx,.txt';
      input.onchange = (e) => {
        if (e.target.files) {
          const newFiles = Array.from(e.target.files).map((f) => ({
            name: f.name,
            size: f.size,
          }));
          setResumes((prev) => [...prev, ...newFiles]);
        }
      };
    }
    input.click();
  };

  const handleRemoveResume = (index) => {
    setResumes((prev) => prev.filter((_, i) => i !== index));
  };

  const handleAnalyze = () => {
    if (!jdFile || resumes.length === 0) return;
    navigate('/analyzing');
  };

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
                  {(jdFile.size / (1024 * 1024)).toFixed(2)} MB • Ready
                </p>
              </div>
            ) : (
              <div>
                <p className="font-label-md text-label-md text-on-surface mb-2">Drag & drop Job Description</p>
                <p className="font-label-sm text-label-sm text-on-surface-variant mb-6">
                  Supports PDF, DOCX, TXT (Max 5MB)
                </p>
                <button className="px-6 py-2 rounded-full border border-white/10 bg-transparent text-on-surface hover:bg-white/5 hover:border-white/40 transition-all font-label-md text-label-md cursor-pointer">
                  Browse Files
                </button>
              </div>
            )}
          </div>
        </GlassCard>

        {/* Candidate Resumes Upload */}
        <GlassCard className="p-6 flex flex-col min-h-[350px]">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-headline-md text-headline-md text-on-surface">Candidate Resumes</h2>
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
            {resumes.length > 0 ? (
              <div>
                <p className="font-label-md text-label-md text-primary font-semibold mb-1">
                  {resumes.length} {resumes.length === 1 ? 'Resume' : 'Resumes'} Added
                </p>
                <p className="font-label-sm text-label-sm text-on-surface-variant">
                  Click to add more or browse files
                </p>
              </div>
            ) : (
              <div>
                <p className="font-label-md text-label-md text-on-surface mb-2">Drag & drop Resume batch</p>
                <p className="font-label-sm text-label-sm text-on-surface-variant mb-6">
                  Upload up to 10 files (PDF, DOCX, TXT)
                </p>
                <button className="px-6 py-2 rounded-full border border-white/10 bg-transparent text-on-surface hover:bg-white/5 hover:border-white/40 transition-all font-label-md text-label-md cursor-pointer">
                  Browse Files
                </button>
              </div>
            )}
          </div>
        </GlassCard>
      </section>

      {/* Files List Panel (Only visible when files are added) */}
      {(jdFile || resumes.length > 0) && (
        <section className="animate-fade-in">
          <GlassCard className="p-6">
            <h3 className="font-headline-md text-headline-md text-on-surface mb-6">Added Documents</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/10 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-widest">
                    <th className="pb-3">File Name</th>
                    <th className="pb-3">Type</th>
                    <th className="pb-3">Size</th>
                    <th className="pb-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="font-body-md text-body-md divide-y divide-white/5">
                  {jdFile && (
                    <tr className="hover:bg-white/5 transition-colors">
                      <td className="py-4 font-semibold text-primary flex items-center gap-2">
                        <span className="material-symbols-outlined text-[20px]">assignment_turned_in</span>
                        {jdFile.name}
                      </td>
                      <td className="py-4 text-on-surface-variant">Job Description</td>
                      <td className="py-4 text-on-surface-variant">
                        {(jdFile.size / (1024 * 1024)).toFixed(2)} MB
                      </td>
                      <td className="py-4 text-right">
                        <button
                          onClick={() => setJdFile(null)}
                          className="text-error hover:text-red-400 font-semibold cursor-pointer active:scale-95"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  )}
                  {resumes.map((file, index) => (
                    <tr key={index} className="hover:bg-white/5 transition-colors">
                      <td className="py-4 flex items-center gap-2">
                        <span className="material-symbols-outlined text-[20px] text-on-surface-variant">description</span>
                        {file.name}
                      </td>
                      <td className="py-4 text-on-surface-variant">Resume</td>
                      <td className="py-4 text-on-surface-variant">
                        {(file.size / (1024 * 1024)).toFixed(2)} MB
                      </td>
                      <td className="py-4 text-right">
                        <button
                          onClick={() => handleRemoveResume(index)}
                          className="text-error hover:text-red-400 font-semibold cursor-pointer active:scale-95"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-8 flex justify-end">
              <button
                onClick={handleAnalyze}
                disabled={!jdFile || resumes.length === 0}
                className={`glow-btn px-10 py-4 rounded-xl font-label-md text-label-md uppercase tracking-wider flex items-center gap-2 cursor-pointer ${
                  (!jdFile || resumes.length === 0) ? 'opacity-40 cursor-not-allowed' : ''
                }`}
              >
                <span className="material-symbols-outlined">analytics</span>
                Analyze Candidates
              </button>
            </div>
          </GlassCard>
        </section>
      )}
    </div>
  );
};

export default SourcingDashboard;
