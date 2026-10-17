import React from 'react';
import { PlatformStatus, SafetyStatus } from '../types';

interface HeaderHUDProps {
  activeTab: 'composer' | 'calendar' | 'analytics' | 'settings';
  setActiveTab: (tab: 'composer' | 'calendar' | 'analytics' | 'settings') => void;
  safety: SafetyStatus | null;
  platforms: Record<string, PlatformStatus>;
  onRefreshCookies: () => void;
  isRefreshing: boolean;
}

export const HeaderHUD: React.FC<HeaderHUDProps> = ({
  activeTab,
  setActiveTab,
  safety,
  platforms,
  onRefreshCookies,
  isRefreshing,
}) => {
  const formatCooldown = (seconds: number) => {
    if (seconds <= 0) return 'Ready';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <header className="top-nav" id="top-nav-hud">
      <div className="brand-section">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent-cyan)' }}>
          <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
          <polyline points="2 17 12 22 22 17"></polyline>
          <polyline points="2 12 12 17 22 12"></polyline>
        </svg>
        <span className="brand-title">OmniMCP Pro</span>
        <span className="brand-badge">v1.0.0</span>
      </div>

      <nav className="nav-tabs" id="navigation-tabs">
        <button
          id="tab-btn-composer"
          className={`nav-tab-btn ${activeTab === 'composer' ? 'active' : ''}`}
          onClick={() => setActiveTab('composer')}
        >
          Omni Composer
        </button>
        <button
          id="tab-btn-calendar"
          className={`nav-tab-btn ${activeTab === 'calendar' ? 'active' : ''}`}
          onClick={() => setActiveTab('calendar')}
        >
          7-Day Calendar
        </button>
        <button
          id="tab-btn-analytics"
          className={`nav-tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          Reach Analytics
        </button>
        <button
          id="tab-btn-settings"
          className={`nav-tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          Safety & Sessions
        </button>
      </nav>

      <div className="hud-safety">
        {/* Platform Status Dots */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {['linkedin', 'twitter', 'wordpress', 'threads', 'facebook'].map((p) => {
            const isConf = platforms[p]?.configured;
            return (
              <div
                key={p}
                title={`${p.toUpperCase()}: ${isConf ? 'Connected' : 'Not configured'}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '11px',
                  color: isConf ? 'var(--text-secondary)' : 'var(--text-muted)',
                  cursor: 'pointer',
                }}
                onClick={() => setActiveTab('settings')}
              >
                <span className={`pulse-dot ${isConf ? 'pulse-green' : 'pulse-amber'}`} />
                <span style={{ textTransform: 'capitalize' }}>{p === 'wordpress' ? 'WP' : p}</span>
              </div>
            );
          })}
        </div>

        {/* Safety Guard: Cooldown */}
        <div className="hud-metric-pill" title="Anti-Ban Cooldown timer (180s minimum between live posts)">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
          <span style={{ color: safety?.is_on_cooldown ? 'var(--accent-purple)' : 'var(--accent-green)' }}>
            {safety ? formatCooldown(safety.cooldown_remaining_seconds) : '...'}
          </span>
        </div>

        {/* Safety Guard: Daily Limit */}
        <div className="hud-metric-pill" title="Daily LinkedIn post quota (max 6 posts/day)">
          <span style={{ color: 'var(--text-muted)' }}>Daily:</span>
          <span style={{ color: (safety?.posts_today || 0) >= (safety?.daily_limit || 6) ? 'var(--accent-rose)' : 'var(--text-primary)' }}>
            {safety ? `${safety.posts_today}/${safety.daily_limit}` : '0/6'}
          </span>
        </div>

        {/* Write Gate Switch Indicator */}
        <div
          className="hud-metric-pill"
          style={{
            borderColor: safety?.write_enabled_in_env ? 'rgba(16, 185, 129, 0.4)' : 'rgba(245, 158, 11, 0.4)',
          }}
          title={safety?.write_enabled_in_env ? 'Live mutations enabled in .env' : 'Preview / Dry-Run only (OMNI_WRITE_ENABLED!=true)'}
        >
          <span style={{ fontSize: '10px', textTransform: 'uppercase', color: safety?.write_enabled_in_env ? 'var(--accent-green)' : 'var(--accent-amber)' }}>
            {safety?.write_enabled_in_env ? 'WRITE ON' : 'PREVIEW ONLY'}
          </span>
        </div>

        {/* Refresh Chrome Session Button */}
        <button
          id="btn-refresh-chrome-session"
          className="btn-secondary"
          style={{ padding: '6px 12px', fontSize: '12px' }}
          onClick={onRefreshCookies}
          disabled={isRefreshing}
          title="Extract fresh session cookies from Google Chrome"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={isRefreshing ? 'animate-spin' : ''}>
            <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path>
          </svg>
          {isRefreshing ? 'Refreshing...' : 'Sync Chrome'}
        </button>
      </div>
    </header>
  );
};
