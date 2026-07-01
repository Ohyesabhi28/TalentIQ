import React, { useState } from 'react';
import GlassCard from '../components/common/GlassCard';
import mockData from '../data/mockData.json';

const ExportCenter = () => {
  const [downloading, setDownloading] = useState({ excel: false, pdf: false, json: false });
  const [notification, setNotification] = useState(null);

  const triggerNotification = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 3500);
  };

  const handleDownload = async (format) => {
    setDownloading(prev => ({ ...prev, [format]: true }));
    const mockJobId = "00000000-0000-0000-0000-000000000000";
    
    try {
      if (format === 'json') {
        // Fetch JSON export from backend or fallback
        try {
          const response = await fetch(`http://localhost:8000/v1/analysis/jobs/${mockJobId}/export/json`);
          if (response.ok) {
            const data = await response.json();
            downloadBlob(JSON.stringify(data, null, 2), 'talent_iq_export.json', 'application/json');
            triggerNotification("JSON configuration downloaded successfully!");
            setDownloading(prev => ({ ...prev, [format]: false }));
            return;
          }
        } catch (e) {
          console.warn("Backend not accessible, generating client-side JSON export:", e);
        }
        // Client-side fallback
        downloadBlob(JSON.stringify(mockData, null, 2), 'talent_iq_mock_export.json', 'application/json');
        triggerNotification("JSON configuration downloaded successfully!");
      } 
      
      else if (format === 'excel') {
        // Fetch Excel export from backend or fallback
        try {
          const response = await fetch(`http://localhost:8000/v1/analysis/jobs/${mockJobId}/export/excel`);
          if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `talent_iq_rankings_${mockJobId}.xlsx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            triggerNotification("Excel spreadsheet downloaded successfully!");
            setDownloading(prev => ({ ...prev, [format]: false }));
            return;
          }
        } catch (e) {
          console.warn("Backend not accessible, generating client-side Excel CSV fallback:", e);
        }
        
        // Client-side fallback (CSV format named as CSV)
        const csvContent = "Rank,Candidate Name,Overall Score,Recommendation\n" + 
          mockData.candidates.map((c, i) => `${i+1},"${c.name}",${c.score},"${c.matchType}"`).join('\n');
        downloadBlob(csvContent, 'talent_iq_rankings.csv', 'text/csv');
        triggerNotification("Excel-compatible CSV downloaded successfully!");
      } 
      
      else if (format === 'pdf') {
        // Fetch PDF export from backend or fallback
        try {
          const response = await fetch(`http://localhost:8000/v1/analysis/jobs/${mockJobId}/export/pdf`);
          if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `talent_iq_report_${mockJobId}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            triggerNotification("Executive PDF report downloaded successfully!");
            setDownloading(prev => ({ ...prev, [format]: false }));
            return;
          }
        } catch (e) {
          console.warn("Backend not accessible, generating client-side report fallback:", e);
        }
        
        // Client-side fallback: trigger window print for the report page
        triggerNotification("Backend export unavailable. Opening print dialog...", "warning");
        setTimeout(() => {
          window.print();
        }, 1000);
      }
    } catch (err) {
      console.error(err);
      triggerNotification("Download failed. Please ensure the backend server is running.", "error");
    } finally {
      setDownloading(prev => ({ ...prev, [format]: false }));
    }
  };

  const downloadBlob = (content, filename, contentType) => {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <header className="space-y-1.5">
        <span className="text-primary font-bold tracking-widest text-[10px] uppercase block">
          Platform Export Control
        </span>
        <h1 className="text-headline-lg font-bold text-white tracking-tight">Export &amp; Submission Center</h1>
        <p className="text-on-surface-variant font-light text-sm max-w-2xl leading-relaxed">
          Generate, compile, and download polished recruiter-ready reports and structured configurations directly from your current active pipeline.
        </p>
      </header>

      {/* Grid of Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Excel */}
        <GlassCard className="p-6 md:p-8 flex flex-col justify-between items-start space-y-6 relative overflow-hidden border-t-4 border-t-[#4ae176]">
          <div className="space-y-3">
            <div className="h-12 w-12 rounded-xl bg-[#4ae176]/10 flex items-center justify-center border border-[#4ae176]/20 text-[#4ae176]">
              <span className="material-symbols-outlined text-2xl">table_chart</span>
            </div>
            <h3 className="text-xl font-bold text-white">Ranked Candidate Spreadsheet</h3>
            <p className="text-xs text-on-surface-variant leading-relaxed font-light">
              Detailed candidate scorecards, skill metrics, semantic similarity scores, education, and interview focus areas structured for spreadsheet reviews.
            </p>
          </div>
          <button
            onClick={() => handleDownload('excel')}
            disabled={downloading.excel}
            className="primary-btn w-full py-2.5 rounded-lg font-label-md text-label-md cursor-pointer flex items-center justify-center gap-2 active:scale-95 transition-transform"
          >
            {downloading.excel ? (
              <>
                <span className="material-symbols-outlined text-[18px] animate-spin">sync</span>
                Compiling...
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-[18px]">download</span>
                Download Excel (.xlsx)
              </>
            )}
          </button>
        </GlassCard>

        {/* PDF */}
        <GlassCard className="p-6 md:p-8 flex flex-col justify-between items-start space-y-6 relative overflow-hidden border-t-4 border-t-primary">
          <div className="space-y-3">
            <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20 text-primary">
              <span className="material-symbols-outlined text-2xl">picture_as_pdf</span>
            </div>
            <h3 className="text-xl font-bold text-white">Executive Hiring Dossier</h3>
            <p className="text-xs text-on-surface-variant leading-relaxed font-light">
              Polished PDF report with custom Cover Page, role requirements summary, aggregate statistics, detailed gap analysis, and candidate matching scores.
            </p>
          </div>
          <button
            onClick={() => handleDownload('pdf')}
            disabled={downloading.pdf}
            className="primary-btn w-full py-2.5 rounded-lg font-label-md text-label-md cursor-pointer flex items-center justify-center gap-2 active:scale-95 transition-transform"
          >
            {downloading.pdf ? (
              <>
                <span className="material-symbols-outlined text-[18px] animate-spin">sync</span>
                Generating...
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-[18px]">download</span>
                Download Report (PDF)
              </>
            )}
          </button>
        </GlassCard>

        {/* JSON */}
        <GlassCard className="p-6 md:p-8 flex flex-col justify-between items-start space-y-6 relative overflow-hidden border-t-4 border-t-[#ffb783]">
          <div className="space-y-3">
            <div className="h-12 w-12 rounded-xl bg-[#ffb783]/10 flex items-center justify-center border border-[#ffb783]/20 text-[#ffb783]">
              <span className="material-symbols-outlined text-2xl">settings_ethernet</span>
            </div>
            <h3 className="text-xl font-bold text-white">Platform Submission JSON</h3>
            <p className="text-xs text-on-surface-variant leading-relaxed font-light">
              Complete structured JSON export containing job descriptions, parsed profiles, raw scores, and explainability recommendations for platform portability.
            </p>
          </div>
          <button
            onClick={() => handleDownload('json')}
            disabled={downloading.json}
            className="primary-btn w-full py-2.5 rounded-lg font-label-md text-label-md cursor-pointer flex items-center justify-center gap-2 active:scale-95 transition-transform"
          >
            {downloading.json ? (
              <>
                <span className="material-symbols-outlined text-[18px] animate-spin">sync</span>
                Packing JSON...
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-[18px]">download</span>
                Download Config (JSON)
              </>
            )}
          </button>
        </GlassCard>
      </div>

      {/* Toast Notification */}
      {notification && (
        <div className="fixed bottom-6 right-6 z-50 animate-[fadeInUp_0.3s_ease-out]">
          <div className={`border px-5 py-3 rounded-xl shadow-2xl flex items-center gap-3 text-sm font-medium max-w-sm ${
            notification.type === 'error' 
              ? 'bg-red-950/90 border-red-500/30 text-red-200' 
              : notification.type === 'warning' 
              ? 'bg-amber-950/90 border-amber-500/30 text-amber-200'
              : 'bg-surface-container border-primary/20 text-on-surface'
          }`}>
            <span className="material-symbols-outlined text-[18px] shrink-0">
              {notification.type === 'error' ? 'error' : notification.type === 'warning' ? 'warning' : 'verified'}
            </span>
            {notification.msg}
          </div>
        </div>
      )}
    </div>
  );
};

export default ExportCenter;
