import React, { useState } from 'react';
import mockData from '../data/mockData.json';

const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    setIsLoading(true);
    // Simulate auth delay
    setTimeout(() => {
      setIsLoading(false);
      onLogin({ email, name: email.split('@')[0].replace(/[._]/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) });
    }, 1200);
  };

  const handleDemoLogin = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      onLogin({ email: 'alex@talentai.com', name: mockData.currentUser.name });
    }, 900);
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center relative overflow-hidden">
      {/* Animated background particles */}
      <div className="particles-container">
        <div className="particle w-4 h-4 left-[10%] top-[20%] animate-[float_15s_infinite_linear]"></div>
        <div className="particle w-2 h-2 left-[80%] top-[40%] animate-[float_22s_infinite_linear]"></div>
        <div className="particle w-6 h-6 left-[30%] top-[70%] animate-[float_18s_infinite_linear]"></div>
        <div className="particle w-3 h-3 left-[70%] top-[10%] animate-[float_25s_infinite_linear]"></div>
        <div className="particle w-5 h-5 left-[55%] top-[85%] animate-[float_20s_infinite_linear]"></div>
      </div>

      {/* Glow orbs */}
      <div className="absolute top-[-200px] left-[-200px] w-[600px] h-[600px] rounded-full bg-primary/5 blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-[-200px] right-[-200px] w-[600px] h-[600px] rounded-full bg-secondary/5 blur-3xl pointer-events-none"></div>

      <div className="relative z-10 w-full max-w-md px-6">
        {/* Logo & header */}
        <div className="text-center mb-10 space-y-3">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-primary/10 border border-primary/30 mb-2 shadow-[0_0_30px_rgba(192,193,255,0.15)]">
            <span className="material-symbols-outlined text-primary text-3xl">smart_toy</span>
          </div>
          <h1 className="text-headline-lg font-bold text-white tracking-tight">TalentAI</h1>
          <p className="text-on-surface-variant text-sm font-light">
            Executive Recruiter Platform — Sign in to continue
          </p>
        </div>

        {/* Login card */}
        <div className="glass-card p-8 space-y-6 border border-white/10 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3">
                <span className="material-symbols-outlined text-[16px]">error</span>
                {error}
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-label-sm text-on-surface-variant block font-medium tracking-wide uppercase">
                Work Email
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-on-surface-variant/60 text-[18px]">mail</span>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  className="w-full custom-input pl-10 pr-4 py-3 text-sm text-white placeholder:text-on-surface-variant/40 rounded-lg"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-label-sm text-on-surface-variant block font-medium tracking-wide uppercase">
                Password
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-on-surface-variant/60 text-[18px]">lock</span>
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full custom-input pl-10 pr-12 py-3 text-sm text-white placeholder:text-on-surface-variant/40 rounded-lg"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant/60 hover:text-on-surface-variant transition-colors cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-on-surface-variant">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input type="checkbox" className="rounded border-white/20 bg-surface-container accent-primary" />
                Remember me
              </label>
              <button type="button" className="text-primary hover:underline cursor-pointer">Forgot password?</button>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-primary text-on-primary rounded-lg font-label-md text-label-md font-semibold shadow-[0_0_20px_rgba(192,193,255,0.25)] hover:shadow-[0_0_30px_rgba(192,193,255,0.4)] transition-all active:scale-[0.98] cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                  </svg>
                  Signing in...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-[18px]">login</span>
                  Sign In
                </>
              )}
            </button>
          </form>

          <div className="relative flex items-center gap-3">
            <div className="flex-1 h-px bg-white/10"></div>
            <span className="text-on-surface-variant/50 text-xs shrink-0">or</span>
            <div className="flex-1 h-px bg-white/10"></div>
          </div>

          <button
            onClick={handleDemoLogin}
            disabled={isLoading}
            className="w-full py-3 bg-surface-container border border-white/10 hover:border-primary/40 hover:bg-white/5 text-on-surface rounded-lg font-label-md text-label-md transition-all active:scale-[0.98] cursor-pointer disabled:opacity-60 flex items-center justify-center gap-2"
          >
            <span className="material-symbols-outlined text-primary text-[18px]">bolt</span>
            Continue with Demo Account
          </button>
        </div>

        <p className="text-center text-on-surface-variant/40 text-xs mt-6">
          TalentAI © {new Date().getFullYear()} · Enterprise Recruiter Platform
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
