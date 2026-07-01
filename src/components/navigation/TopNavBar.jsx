import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const TopNavBar = ({ onSearch, user, onLogoutClick, onSupportClick }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const getLinkClass = (path) => {
    const isCurrent = location.pathname === path;
    return `h-full flex items-center transition-colors cursor-pointer font-label-md text-label-md py-2 ${
      isCurrent
        ? 'text-primary border-b-2 border-primary font-semibold'
        : 'text-on-surface-variant hover:text-primary'
    }`;
  };

  const initials = user?.name
    ? user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : 'U';

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    if (dropdownOpen) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [dropdownOpen]);

  return (
    <nav className="fixed top-0 w-full z-50 flex items-center justify-between px-margin-mobile md:px-margin-desktop h-16 bg-surface/60 backdrop-blur-xl border-b border-white/10 shadow-sm">
      <div className="flex items-center gap-6">
        <Link to="/" className="font-bold text-xl text-primary tracking-tight">
          TalentAI
        </Link>
        <div className="hidden md:flex items-center bg-surface-container/50 border border-white/5 rounded-full px-4 py-1.5 ml-4 hover:bg-surface-container transition-colors focus-within:border-primary/50 focus-within:bg-surface">
          <span className="material-symbols-outlined text-on-surface-variant text-[18px] mr-2">search</span>
          <input
            className="bg-transparent border-none outline-none text-sm text-on-surface placeholder:text-on-surface-variant/50 w-64 focus:ring-0 px-0"
            placeholder="Search profiles, skills..."
            type="text"
            onChange={(e) => onSearch && onSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="hidden md:flex items-center gap-8 h-full">
        <ul className="flex items-center gap-6 h-full">
          <li className="h-full">
            <Link to="/" className={getLinkClass('/')}>Dashboard</Link>
          </li>
          <li className="h-full">
            <Link to="/results" className={getLinkClass('/results')}>Pipeline</Link>
          </li>
          <li className="h-full">
            <Link to="/analytics" className={getLinkClass('/analytics')}>Analytics</Link>
          </li>
        </ul>
      </div>

      <div className="flex items-center gap-3">
        {/* Notifications */}
        <button className="text-on-surface-variant hover:text-primary transition-colors cursor-pointer active:scale-95 flex items-center justify-center w-9 h-9 rounded-full hover:bg-white/5">
          <span className="material-symbols-outlined text-[20px]">notifications</span>
        </button>

        {/* Help — opens support modal */}
        <button
          onClick={() => onSupportClick && onSupportClick()}
          className="text-on-surface-variant hover:text-primary transition-colors cursor-pointer active:scale-95 flex items-center justify-center w-9 h-9 rounded-full hover:bg-white/5"
        >
          <span className="material-symbols-outlined text-[20px]">help</span>
        </button>

        {/* User avatar with dropdown */}
        <div className="relative ml-1" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen(prev => !prev)}
            className="w-8 h-8 rounded-full bg-primary/15 border border-primary/30 flex items-center justify-center cursor-pointer font-semibold text-[11px] text-primary select-none tracking-wider shadow-[0_0_10px_rgba(192,193,255,0.1)] hover:bg-primary/25 hover:border-primary/50 transition-all active:scale-95"
            title={user?.name || 'Account'}
          >
            {initials}
          </button>

          {/* Dropdown panel */}
          {dropdownOpen && (
            <div className="absolute right-0 top-[calc(100%+10px)] w-56 glass-card border border-white/10 shadow-2xl rounded-xl overflow-hidden z-50 animate-[fadeInUp_0.15s_ease-out]">
              {/* User info header */}
              <div className="px-4 py-3 border-b border-white/10 space-y-0.5">
                <p className="text-sm font-semibold text-white truncate">{user?.name || 'User'}</p>
                <p className="text-xs text-on-surface-variant/70 truncate">{user?.email || ''}</p>
              </div>

              {/* Menu items */}
              <div className="py-1">
                <button
                  onClick={() => { navigate('/'); setDropdownOpen(false); }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-on-surface-variant hover:bg-white/5 hover:text-white transition-colors cursor-pointer text-left"
                >
                  <span className="material-symbols-outlined text-[18px]">dashboard</span>
                  Dashboard
                </button>
                <button
                  onClick={() => { onSupportClick && onSupportClick(); setDropdownOpen(false); }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-on-surface-variant hover:bg-white/5 hover:text-white transition-colors cursor-pointer text-left"
                >
                  <span className="material-symbols-outlined text-[18px]">support_agent</span>
                  Help &amp; Support
                </button>
              </div>

              {/* Logout */}
              <div className="py-1 border-t border-white/10">
                <button
                  onClick={() => { onLogoutClick && onLogoutClick(); setDropdownOpen(false); }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors cursor-pointer text-left"
                >
                  <span className="material-symbols-outlined text-[18px]">logout</span>
                  Sign out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default TopNavBar;
