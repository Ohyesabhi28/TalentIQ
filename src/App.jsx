import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import TopNavBar from './components/navigation/TopNavBar';
import SideNavBar from './components/navigation/SideNavBar';
import SourcingDashboard from './pages/SourcingDashboard';
import AnalyzingLoader from './pages/AnalyzingLoader';
import PipelineResults from './pages/PipelineResults';
import CandidateProfile from './pages/CandidateProfile';
import CandidateComparison from './pages/CandidateComparison';
import SkillGapAnalytics from './pages/SkillGapAnalytics';
import HiringReport from './pages/HiringReport';
import ExportCenter from './pages/ExportCenter';
import LoginPage from './pages/LoginPage';
import mockData from './data/mockData.json';

// Inner component that can use useNavigate (must be inside <Router>)
function AppShell({ user, onLogout }) {
  const navigate = useNavigate();

  const [jdFile, setJdFile] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [activeJobId, setActiveJobId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSupportOpen, setSupportOpen] = useState(false);
  const [isLogoutOpen, setLogoutOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  // Support form states
  const [supportName, setSupportName] = useState('');
  const [supportEmail, setSupportEmail] = useState('');
  const [supportDesc, setSupportDesc] = useState('');

  const showToast = (msg, type = 'success') => {
    setToastMessage({ msg, type });
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleSupportSubmit = (e) => {
    e.preventDefault();
    setSupportOpen(false);
    const ticketId = Math.floor(10000 + Math.random() * 90000);
    showToast(`Support ticket #${ticketId} submitted — our team will contact you shortly.`);
    setSupportName('');
    setSupportEmail('');
    setSupportDesc('');
  };

  const handleConfirmLogout = () => {
    setLogoutOpen(false);
    setJdFile(null);
    setResumes([]);
    setSearchQuery('');
    // Give a brief moment so state clears, then trigger logout → login screen
    setTimeout(() => {
      onLogout();
    }, 300);
  };

  // Dynamically map uploaded resumes to mock candidate profiles
  const getMappedCandidates = () => {
    if (resumes.length === 0) return [];
    return resumes.map((resume, index) => {
      const resumeNameLower = resume.name.toLowerCase();
      let matchedCandidate;

      if (resumeNameLower.includes('sarah') || resumeNameLower.includes('ui') || index === 0) {
        matchedCandidate = mockData.candidates.find(c => c.id === 'sarah-j') || mockData.candidates[0];
      } else if (resumeNameLower.includes('michael') || resumeNameLower.includes('dev') || index === 1) {
        matchedCandidate = mockData.candidates.find(c => c.id === 'michael-c') || mockData.candidates[1];
      } else {
        matchedCandidate = mockData.candidates[index % mockData.candidates.length];
      }

      return { ...matchedCandidate, fileName: resume.name };
    });
  };

  const candidates = getMappedCandidates();

  const filteredCandidates = candidates.filter(candidate => {
    const query = searchQuery.toLowerCase();
    if (!query) return true;
    return (
      candidate.name.toLowerCase().includes(query) ||
      candidate.prevRole.toLowerCase().includes(query) ||
      Object.keys(candidate.skills).some(skill =>
        skill.toLowerCase().includes(query) && candidate.skills[skill] === 'match'
      )
    );
  });

  return (
    <div className="min-h-screen bg-background text-on-background selection:bg-primary-container selection:text-on-primary-container flex flex-col font-sans">
      {/* Particle background */}
      <div className="particles-container">
        <div className="particle w-4 h-4 left-[10%] top-[20%] animate-[float_15s_infinite_linear]"></div>
        <div className="particle w-2 h-2 left-[80%] top-[40%] animate-[float_22s_infinite_linear]"></div>
        <div className="particle w-6 h-6 left-[30%] top-[70%] animate-[float_18s_infinite_linear]"></div>
        <div className="particle w-3 h-3 left-[70%] top-[10%] animate-[float_25s_infinite_linear]"></div>
      </div>

      <TopNavBar
        onSearch={setSearchQuery}
        user={user}
        onSupportClick={() => setSupportOpen(true)}
        onLogoutClick={() => setLogoutOpen(true)}
      />

      <div className="flex flex-1 pt-16">
        <SideNavBar
          onSupportClick={() => setSupportOpen(true)}
          onLogoutClick={() => setLogoutOpen(true)}
        />

        <main className="flex-1 md:ml-64 p-margin-mobile md:p-margin-desktop overflow-x-hidden relative z-10">
          <Routes>
            <Route
              path="/"
              element={
                <SourcingDashboard
                  jdFile={jdFile}
                  setJdFile={setJdFile}
                  resumes={resumes}
                  setResumes={setResumes}
                  activeJobId={activeJobId}
                  setActiveJobId={setActiveJobId}
                />
              }
            />
            <Route path="/analyzing" element={<AnalyzingLoader activeJobId={activeJobId} setActiveJobId={setActiveJobId} />} />
            <Route
              path="/results"
              element={<PipelineResults candidates={filteredCandidates} allCandidatesCount={candidates.length} activeJobId={activeJobId} />}
            />
            <Route
              path="/profile/:id"
              element={<CandidateProfile candidates={candidates} activeJobId={activeJobId} />}
            />
            <Route
              path="/comparison"
              element={<CandidateComparison candidates={candidates} activeJobId={activeJobId} />}
            />
            <Route path="/analytics" element={<SkillGapAnalytics activeJobId={activeJobId} />} />
            <Route
              path="/report"
              element={<HiringReport candidates={candidates} activeJobId={activeJobId} />}
            />
            <Route path="/export" element={<ExportCenter activeJobId={activeJobId} />} />
          </Routes>
        </main>
      </div>

      {/* ── Support Modal ──────────────────────────────────────── */}
      {isSupportOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md"
          onClick={(e) => { if (e.target === e.currentTarget) setSupportOpen(false); }}
        >
          <div className="w-full max-w-lg glass-card p-6 md:p-8 space-y-6 relative border border-white/10 shadow-2xl">
            <button
              onClick={() => setSupportOpen(false)}
              className="absolute top-4 right-4 text-on-surface-variant hover:text-white transition-colors cursor-pointer"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
            <div className="space-y-1">
              <h3 className="text-headline-md font-bold text-white tracking-tight flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">support_agent</span>
                Help &amp; Support
              </h3>
              <p className="text-on-surface-variant text-sm font-light">
                Submit a ticket or issue to our technical support team.
              </p>
            </div>
            <form onSubmit={handleSupportSubmit} className="space-y-4">
              <div className="space-y-1">
                <label className="text-label-sm text-on-surface-variant block font-medium">Your Name</label>
                <input
                  type="text"
                  required
                  value={supportName}
                  onChange={(e) => setSupportName(e.target.value)}
                  placeholder="Enter your name"
                  className="w-full custom-input px-4 py-2.5 text-sm text-white rounded-lg"
                />
              </div>
              <div className="space-y-1">
                <label className="text-label-sm text-on-surface-variant block font-medium">Email Address</label>
                <input
                  type="email"
                  required
                  value={supportEmail}
                  onChange={(e) => setSupportEmail(e.target.value)}
                  placeholder="Enter email address"
                  className="w-full custom-input px-4 py-2.5 text-sm text-white rounded-lg"
                />
              </div>
              <div className="space-y-1">
                <label className="text-label-sm text-on-surface-variant block font-medium">Description of Issue</label>
                <textarea
                  rows="4"
                  required
                  value={supportDesc}
                  onChange={(e) => setSupportDesc(e.target.value)}
                  placeholder="What do you need help with?"
                  className="w-full custom-input px-4 py-2.5 text-sm text-white resize-none rounded-lg"
                ></textarea>
              </div>
              <div className="pt-2 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setSupportOpen(false)}
                  className="px-5 py-2.5 rounded-lg border border-white/10 hover:bg-white/5 text-on-surface-variant font-label-md text-label-md cursor-pointer transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2.5 rounded-lg bg-primary text-on-primary font-label-md text-label-md cursor-pointer shadow-[0_0_15px_rgba(192,193,255,0.3)] hover:shadow-[0_0_25px_rgba(192,193,255,0.5)] transition-all"
                >
                  Submit Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Logout Modal ───────────────────────────────────────── */}
      {isLogoutOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md"
          onClick={(e) => { if (e.target === e.currentTarget) setLogoutOpen(false); }}
        >
          <div className="w-full max-w-md glass-card p-6 md:p-8 space-y-6 relative border border-white/10 shadow-2xl">
            <button
              onClick={() => setLogoutOpen(false)}
              className="absolute top-4 right-4 text-on-surface-variant hover:text-white transition-colors cursor-pointer"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
            <div className="space-y-3 text-center">
              <div className="h-14 w-14 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center mx-auto">
                <span className="material-symbols-outlined text-red-400 text-2xl">logout</span>
              </div>
              <h3 className="text-headline-md font-bold text-white tracking-tight">Confirm Logout</h3>
              <p className="text-on-surface-variant text-sm font-light leading-relaxed">
                Are you sure you want to log out? You will be returned to the login screen and all uploaded files will be cleared from this session.
              </p>
            </div>
            <div className="flex gap-4">
              <button
                onClick={() => setLogoutOpen(false)}
                className="flex-1 py-2.5 rounded-lg border border-white/10 hover:bg-white/5 text-on-surface-variant font-label-md text-label-md cursor-pointer transition-colors"
              >
                Stay Logged In
              </button>
              <button
                onClick={handleConfirmLogout}
                className="flex-1 py-2.5 rounded-lg bg-red-500 hover:bg-red-600 text-white font-label-md text-label-md cursor-pointer transition-colors active:scale-95"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Toast ─────────────────────────────────────────────── */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-[60] animate-[fadeInUp_0.3s_ease-out]">
          <div className="bg-surface-container border border-primary/20 text-on-surface px-5 py-3 rounded-xl shadow-2xl flex items-center gap-3 text-sm font-medium max-w-sm">
            <span className="material-symbols-outlined text-primary text-[18px] shrink-0">verified</span>
            {toastMessage.msg}
          </div>
        </div>
      )}
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null); // null = logged out

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  // Show login page when not authenticated
  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  // Show the full app when authenticated
  return (
    <Router>
      <AppShell user={user} onLogout={handleLogout} />
    </Router>
  );
}

export default App;
