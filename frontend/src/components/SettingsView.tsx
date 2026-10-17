import React, { useState } from 'react';
import { CircleCheck, Cookie, ExternalLink, KeyRound, Lock, Plug, RefreshCw, ShieldCheck } from 'lucide-react';
import { PlatformStatus, SafetyStatus } from '../types';
import { PageHeader, PlatformGlyph, useToast } from './ui';

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
  const toast = useToast();
  const [liAt, setLiAt] = useState('');
  const [jsessionId, setJsessionId] = useState('');
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!liAt.trim() || !jsessionId.trim()) return;
    onUpdateCookies(liAt, jsessionId);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  const handleOAuth = async () => {
    setIsConnecting(true);
    try {
      const res = await fetch('/api/auth/linkedin/oauth/url');
      const data = await res.json();
      if (data.auth_url) {
        window.location.href = data.auth_url;
        return;
      }
      toast(data.detail || 'Configure LINKEDIN_CLIENT_ID in your .env first.', 'error');
    } catch (e) {
      toast(`Could not reach backend OAuth endpoint: ${e}`, 'error');
    }
    setIsConnecting(false);
  };

  const platformEntries = Object.entries(platforms);

  return (
    <>
      <PageHeader
        eyebrow={
          <>
            <Lock size={13} aria-hidden="true" /> Local-first
          </>
        }
        title="Safety & sessions"
        description="Session tokens never leave your machine. Everything is stored in ~/.omnimcp/."
      />

      <div className="settings-stack">
        <section className="card" aria-labelledby="guard-title">
          <div className="card-header">
            <div>
              <h2 id="guard-title" className="card-title">
                <ShieldCheck size={16} aria-hidden="true" />
                Anti-ban guard
              </h2>
              <p className="card-subtitle">Hard limits enforced on every live write.</p>
            </div>
            <span className={`badge ${safety?.write_enabled_in_env ? 'badge-ok' : 'badge-warn'}`}>
              {safety?.write_enabled_in_env ? 'Live mutations enabled' : 'Preview mode only'}
            </span>
          </div>
          <div className="metric-grid">
            <div>
              <div className="stat-label">Mandatory cooldown</div>
              <div className="metric-value">
                {safety?.cooldown_seconds ?? 180}s
                <span className="muted mono" style={{ fontSize: 12, fontWeight: 400, marginLeft: 8 }}>
                  {safety?.cooldown_remaining_seconds ?? 0}s left
                </span>
              </div>
              <div className="hint" style={{ marginTop: 2 }}>
                {safety?.is_on_cooldown ? 'Cooldown in progress' : 'Ready to post'}
              </div>
            </div>
            <div>
              <div className="stat-label">Daily frequency cap</div>
              <div className="metric-value">
                {safety ? `${safety.posts_today} / ${safety.daily_limit}` : '0 / 6'}
              </div>
              <div className="hint" style={{ marginTop: 2 }}>
                Posts today
              </div>
            </div>
            <div>
              <div className="stat-label">Human jitter delay</div>
              <div className="metric-value">1.5–3.5s</div>
              <div className="hint" style={{ marginTop: 2 }}>
                Randomized typing interval
              </div>
            </div>
          </div>
        </section>

        <section className="card" aria-labelledby="cookies-title">
          <div className="card-header">
            <div>
              <h2 id="cookies-title" className="card-title">
                <Cookie size={16} aria-hidden="true" />
                LinkedIn session cookies
              </h2>
              <p className="card-subtitle">Powers the sub-500ms Voyager REST API and Patchright automation.</p>
            </div>
            <button type="button" className="btn btn-secondary btn-sm" onClick={onRefreshFromChrome} disabled={isRefreshing}>
              <RefreshCw size={14} className={isRefreshing ? 'spin' : ''} aria-hidden="true" />
              {isRefreshing ? 'Extracting…' : 'Auto-sync from Chrome'}
            </button>
          </div>
          <form onSubmit={handleSave}>
            <div className="card-body form-grid cols-2">
              <div className="field">
                <label htmlFor="li-at" className="label">
                  li_at
                </label>
                <input
                  id="li-at"
                  type="password"
                  autoComplete="off"
                  className="input input-mono"
                  placeholder="AQED…"
                  value={liAt}
                  onChange={(e) => setLiAt(e.target.value)}
                />
              </div>
              <div className="field">
                <label htmlFor="jsessionid" className="label">
                  JSESSIONID / csrf-token
                </label>
                <input
                  id="jsessionid"
                  type="password"
                  autoComplete="off"
                  className="input input-mono"
                  placeholder='"ajax:…"'
                  value={jsessionId}
                  onChange={(e) => setJsessionId(e.target.value)}
                />
              </div>
            </div>
            <div className="card-footer">
              <span className="hint" role="status">
                {savedSuccess ? (
                  <span className="row text-ok">
                    <CircleCheck size={14} aria-hidden="true" /> Saved to ~/.omnimcp/cookies.json
                  </span>
                ) : (
                  'Stored locally and encrypted at rest.'
                )}
              </span>
              <button type="submit" className="btn btn-primary" disabled={!liAt || !jsessionId}>
                Save cookies
              </button>
            </div>
          </form>
        </section>

        <section className="card" aria-labelledby="oauth-title">
          <div className="card-header">
            <div>
              <h2 id="oauth-title" className="card-title">
                <KeyRound size={16} aria-hidden="true" />
                Official LinkedIn app (OAuth 2.0)
              </h2>
              <p className="card-subtitle">Compliant UGC publishing and media uploads via the Consumer Solutions Platform.</p>
            </div>
          </div>
          <div className="card-body">
            <ol className="steps">
              <li>
                <span>
                  Create an app at{' '}
                  <a className="text-link" href="https://www.linkedin.com/developers/apps" target="_blank" rel="noreferrer">
                    linkedin.com/developers/apps
                    <ExternalLink size={11} style={{ marginLeft: 3, verticalAlign: 'baseline' }} aria-hidden="true" />
                  </a>
                </span>
              </li>
              <li>
                <span>
                  Under <strong>Products</strong>, add <strong>Sign In with LinkedIn using OpenID Connect</strong> and{' '}
                  <strong>Share on LinkedIn</strong>.
                </span>
              </li>
              <li>
                <span>
                  Under <strong>Auth</strong>, add the redirect URL{' '}
                  <code className="code">http://localhost:8000/api/auth/linkedin/callback</code>
                </span>
              </li>
              <li>
                <span>
                  Authorize below to auto-save your <code className="code">LINKEDIN_ACCESS_TOKEN</code>.
                </span>
              </li>
            </ol>
          </div>
          <div className="card-footer">
            <span className="hint mono">openid · profile · email · w_member_social</span>
            <button type="button" className="btn btn-primary" onClick={handleOAuth} disabled={isConnecting}>
              <PlatformGlyph id="linkedin" />
              {isConnecting ? 'Redirecting…' : 'Connect with LinkedIn'}
            </button>
          </div>
        </section>

        <section className="card" aria-labelledby="adapters-title">
          <div className="card-header">
            <div>
              <h2 id="adapters-title" className="card-title">
                <Plug size={16} aria-hidden="true" />
                Platform adapters
              </h2>
              <p className="card-subtitle">Connection health for every channel.</p>
            </div>
          </div>
          {platformEntries.length === 0 ? (
            <div className="card-body">
              <p className="hint">No adapters reported yet. Start the backend to see live status.</p>
            </div>
          ) : (
            <ul className="adapter-list">
              {platformEntries.map(([key, p]) => (
                <li key={key} className="adapter-row">
                  <PlatformGlyph id={key} size="lg" />
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <div className="adapter-name">{p.name}</div>
                    <div className="adapter-meta">
                      {p.auth_info?.name ? p.auth_info.name : p.configured ? 'Authenticated' : 'Add credentials to .env'}
                    </div>
                  </div>
                  <span className={`badge ${p.configured ? 'badge-ok' : ''}`}>
                    <span className={`dot ${p.configured ? 'dot-ok' : 'dot-muted'}`} aria-hidden="true" />
                    {p.configured ? 'Ready' : 'Optional'}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </>
  );
};
