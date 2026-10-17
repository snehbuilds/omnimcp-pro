import React, { useState } from 'react';
import { PlatformStatus, SafetyStatus } from '../types';

interface SettingsViewProps {
  safety: SafetyStatus | null;
  platforms: Record<string, PlatformStatus>;
  onUpdateCookies: (liAt: string, jsessionId: string) => void;
  onRefreshFromChrome: () => void;
  isRefreshing: boolean;
}

export const SettingsView: React.FC<SettingsViewProps> = ({
  safety,
  platforms,
  onUpdateCookies,
  onRefreshFromChrome,
  isRefreshing,
}) => {
  const [liAt, setLiAt] = useState('');
  const [jsessionId, setJsessionId] = useState('');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!liAt.trim() || !jsessionId.trim()) return;
    onUpdateCookies(liAt, jsessionId);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '22px', fontWeight: 700, fontFamily: 'var(--font-display)', marginBottom: '8px' }}>
        Safety & Credential Control Center
      </h2>
      <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '24px' }}>
        Local-first credential isolation: Session tokens never leave your local environment and are stored securely in ~/.omnimcp/.
      </p>

      {/* Safety Guard Status Card */}
      <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, fontFamily: 'var(--font-display)', marginBottom: '14px' }}>
          Strict Anti-Ban Guard
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>MANDATORY COOLDOWN</div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--accent-purple)', marginTop: '4px' }}>
              {safety?.cooldown_seconds || 180}s ({safety?.cooldown_remaining_seconds || 0}s left)
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              {safety?.is_on_cooldown ? 'Active cooldown in progress' : 'Ready to post'}
            </div>
          </div>

          <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>DAILY FREQUENCY CAP</div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--accent-cyan)', marginTop: '4px' }}>
              {safety ? `${safety.posts_today} / ${safety.daily_limit}` : '0 / 6'} Posts
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              {safety?.write_enabled_in_env ? 'Live mutations enabled' : 'Preview mode only'}
            </div>
          </div>

          <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>HUMAN JITTER DELAY</div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--accent-green)', marginTop: '4px' }}>
              1.5s – 3.5s
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Randomized typing interval
            </div>
          </div>
        </div>
      </div>

      {/* LinkedIn Session Cookies Management */}
      <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, fontFamily: 'var(--font-display)' }}>
              LinkedIn Session Cookies (li_at & JSESSIONID)
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Required for sub-500ms Voyager REST API and Patchright browser automation.
            </p>
          </div>

          <button
            type="button"
            className="btn-secondary"
            onClick={onRefreshFromChrome}
            disabled={isRefreshing}
          >
            {isRefreshing ? 'Extracting...' : 'Auto-Sync from Chrome'}
          </button>
        </div>

        <form onSubmit={handleSave}>
          <div style={{ marginBottom: '14px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
              li_at Cookie:
            </label>
            <input
              type="password"
              className="composer-textarea"
              style={{ minHeight: 'auto', padding: '10px', fontSize: '13px', fontFamily: 'var(--font-mono)' }}
              placeholder="AQED... (paste li_at cookie here)"
              value={liAt}
              onChange={(e) => setLiAt(e.target.value)}
            />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
              JSESSIONID Cookie (or csrf-token):
            </label>
            <input
              type="password"
              className="composer-textarea"
              style={{ minHeight: 'auto', padding: '10px', fontSize: '13px', fontFamily: 'var(--font-mono)' }}
              placeholder='"ajax:..." (paste JSESSIONID here)'
              value={jsessionId}
              onChange={(e) => setJsessionId(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {savedSuccess ? (
              <span style={{ fontSize: '12px', color: 'var(--accent-green)', fontWeight: 600 }}>
                ✓ Cookies saved to ~/.omnimcp/cookies.json
              </span>
            ) : <span />}

            <button type="submit" className="btn-primary" disabled={!liAt || !jsessionId}>
              Save Session Cookies
            </button>
          </div>
        </form>
      </div>

      {/* Connected Platforms Health */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, fontFamily: 'var(--font-display)', marginBottom: '14px' }}>
          Platform Adapter Status
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {Object.entries(platforms).map(([key, p]) => (
            <div
              key={key}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '10px 14px',
                background: 'var(--bg-secondary)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className={`pulse-dot ${p.configured ? 'pulse-green' : 'pulse-amber'}`} />
                <span style={{ fontWeight: 600, fontSize: '13px', textTransform: 'capitalize' }}>
                  {p.name}
                </span>
                {p.auth_info?.name && (
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    ({p.auth_info.name})
                  </span>
                )}
              </div>

              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  color: p.configured ? 'var(--accent-green)' : 'var(--text-muted)',
                }}
              >
                {p.configured ? 'Configured & Ready' : 'Optional (Add to .env)'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
