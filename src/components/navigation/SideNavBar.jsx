import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const SideNavBar = ({ onSupportClick, onLogoutClick }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const getLinkClass = (path, icon) => {
    const isCurrent = location.pathname === path;
    return `flex items-center gap-3 px-4 py-3 rounded-lg transition-all cursor-pointer active:translate-x-1 font-label-md text-label-md ${
      isCurrent
        ? 'bg-primary/10 text-primary border-l-4 border-primary font-semibold'
        : 'text-on-surface-variant hover:bg-white/5 hover:text-on-surface'
    }`;
  };

  return (
    <aside className="hidden md:flex flex-col py-6 px-4 bg-surface/60 backdrop-blur-xl fixed left-0 top-16 h-[calc(100vh-64px)] w-64 border-r border-white/10 shadow-lg z-40">
      <div className="mb-8 px-2">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-primary-container/20 flex items-center justify-center border border-primary/30 shrink-0">
            <span className="material-symbols-outlined text-primary">smart_toy</span>
          </div>
          <div>
            <h2 className="font-label-md text-label-md font-bold text-on-surface">Recruiter Copilot</h2>
            <p className="font-label-sm text-label-sm text-on-surface-variant/70">Enterprise Mode</p>
          </div>
        </div>
      </div>
      <button 
        onClick={() => navigate('/')}
        className="mb-6 w-full py-2.5 px-4 bg-primary text-on-primary rounded-lg font-label-md text-label-md shadow-[0_0_15px_rgba(192,193,255,0.3)] hover:shadow-[0_0_20px_rgba(192,193,255,0.5)] transition-all flex items-center justify-center gap-2 border-t border-white/20 active:scale-95 cursor-pointer"
      >
        <span className="material-symbols-outlined text-[18px]">add</span>
        New Search
      </button>
      <nav className="flex-1 flex flex-col gap-2">
        <Link to="/" className={getLinkClass('/', 'search_insights')}>
          <span className="material-symbols-outlined text-[20px]">search_insights</span>
          Sourcing
        </Link>
        <Link to="/results" className={getLinkClass('/results', 'view_column')}>
          <span className="material-symbols-outlined text-[20px]">view_column</span>
          Pipeline
        </Link>
        <Link to="/analytics" className={getLinkClass('/analytics', 'analytics')}>
          <span className="material-symbols-outlined text-[20px]">analytics</span>
          Analytics
        </Link>
        <Link to="/report" className={getLinkClass('/report', 'assignment')}>
          <span className="material-symbols-outlined text-[20px]">assignment</span>
          Hiring Report
        </Link>
        <Link to="/export" className={getLinkClass('/export', 'download')}>
          <span className="material-symbols-outlined text-[20px]">download</span>
          Export Center
        </Link>
      </nav>
      <div className="mt-auto border-t border-white/10 pt-4 flex flex-col gap-2">
        <button 
          onClick={onSupportClick}
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-on-surface-variant hover:bg-white/5 hover:text-on-surface transition-all cursor-pointer font-label-md text-label-md w-full text-left"
        >
          <span className="material-symbols-outlined text-[20px]">support_agent</span>
          Support
        </button>
        <button 
          onClick={onLogoutClick}
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-on-surface-variant hover:bg-white/5 hover:text-on-surface transition-all cursor-pointer font-label-md text-label-md w-full text-left"
        >
          <span className="material-symbols-outlined text-[20px]">logout</span>
          Logout
        </button>
      </div>
    </aside>
  );
};

export default SideNavBar;
