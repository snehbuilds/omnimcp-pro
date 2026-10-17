import React from 'react';
import { ChartColumn, CalendarDays, Layers, PenLine, RefreshCw, ShieldCheck } from 'lucide-react';
import { PlatformStatus, SafetyStatus } from '../types';
import { PLATFORM_IDS, getPlatformMeta } from '../platforms';

export type TabId = 'composer' | 'calendar' | 'analytics' | 'settings';

const NAV_ITEMS: { id: TabId; label: string; short: string; icon: React.ElementType; kbd: string }[] = [
  { id: 'composer', label: 'Composer', short: 'Compose', icon: PenLine, kbd: '1' },
  { id: 'calendar', label: 'Calendar', short: 'Calendar', icon: CalendarDays, kbd: '2' },
  { id: 'analytics', label: 'Analytics', short: 'Analytics', icon: ChartColumn, kbd: '3' },
  { id: 'settings', label: 'Safety & Sessions', short: 'Safety', icon: ShieldCheck, kbd: '4' },
];

interface AppNavigationProps {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  safety: SafetyStatus | null;
  platforms: Record<string, PlatformStatus>;
  onRefreshCookies: () => void;
  isRefreshing: boolean;
}

export const formatCooldown = (seconds: number) => {
  if (seconds <= 0) return 'Ready';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};

const Brand: React.FC = () => (
  <div className="brand">
    <span className="brand-mark" aria-hidden="true">
      <Layers size={16} strokeWidth={2.25} />
    </span>
    <span className="brand-name">OmniMCP</span>
    <span className="brand-version">Pro</span>
  </div>
);

const WriteModeBadge: React.FC<{ safety: SafetyStatus | null }> = ({ safety }) =>
  safety?.write_enabled_in_env ? (
    <span className="badge badge-ok">
      <span className="dot dot-ok dot-live" />
      Live writes
    </span>
  ) : (
    <span className="badge badge-warn">
      <span className="dot dot-warn" />
      Preview only
    </span>
  );

export const AppNavigation: React.FC<AppNavigationProps> = ({
  activeTab,
  setActiveTab,
  safety,
  platforms,
  onRefreshCookies,
  isRefreshing,
}) => {
  const postsToday = safety?.posts_today ?? 0;
  const dailyLimit = safety?.daily_limit ?? 6;
  const quotaPct = Math.min(100, (postsToday / Math.max(1, dailyLimit)) * 100);
  const cooldownTotal = safety?.cooldown_seconds ?? 180;
  const cooldownRemaining = safety?.cooldown_remaining_seconds ?? 0;
  const cooldownPct = cooldownRemaining > 0 ? 100 - (cooldownRemaining / cooldownTotal) * 100 : 100;

  return (
    <>
      <aside className="sidebar" aria-label="Primary">
        <Brand />

        <nav aria-label="Main navigation">
          <div className="nav-section-label">Workspace</div>
          <ul className="nav-list">
            {NAV_ITEMS.map(({ id, label, icon: Icon, kbd }) => (
              <li key={id}>
                <button
                  type="button"
                  className="nav-item"
                  aria-current={activeTab === id ? 'page' : undefined}
                  onClick={() => setActiveTab(id)}
                >
                  <Icon size={16} aria-hidden="true" />
                  {label}
                  <kbd className="nav-kbd">{kbd}</kbd>
                </button>
              </li>
            ))}
          </ul>
        </nav>

        <div>
          <div className="nav-section-label">Channels</div>
          <ul className="connection-list">
            {PLATFORM_IDS.map((p) => {
              const ok = platforms[p]?.configured;
              return (
                <li key={p} className="connection-item">
                  <span className={`dot ${ok ? 'dot-ok' : 'dot-muted'}`} aria-hidden="true" />
                  {getPlatformMeta(p).label}
                  <span className="status-text">{ok ? 'Live' : 'Off'}</span>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="sidebar-footer">
          <div className="safety-widget" aria-label="Safety guard status">
            <div className="safety-row">
              <span>Write gate</span>
              <WriteModeBadge safety={safety} />
            </div>
            <div className="stack-sm">
              <div className="safety-row">
                <span>Cooldown</span>
                <strong className={safety?.is_on_cooldown ? 'text-warn' : 'text-ok'}>
                  {safety ? formatCooldown(cooldownRemaining) : '—'}
                </strong>
              </div>
              <div className="progress" aria-hidden="true">
                <span style={{ width: `${cooldownPct}%`, background: safety?.is_on_cooldown ? 'var(--warning)' : undefined }} />
              </div>
            </div>
            <div className="stack-sm">
              <div className="safety-row">
                <span>Daily quota</span>
                <strong className={postsToday >= dailyLimit ? 'text-danger' : undefined}>
                  {postsToday}/{dailyLimit}
                </strong>
              </div>
              <div className="progress" aria-hidden="true">
                <span style={{ width: `${quotaPct}%`, background: postsToday >= dailyLimit ? 'var(--danger)' : 'var(--text-2)' }} />
              </div>
            </div>
          </div>
          <button type="button" className="btn btn-secondary btn-sm btn-block" onClick={onRefreshCookies} disabled={isRefreshing}>
            <RefreshCw size={14} className={isRefreshing ? 'spin' : ''} aria-hidden="true" />
            {isRefreshing ? 'Syncing session…' : 'Sync Chrome session'}
          </button>
        </div>
      </aside>

      <header className="mobile-topbar">
        <Brand />
        <div className="row">
          <span className="badge badge-mono" aria-label={`Cooldown ${safety ? formatCooldown(cooldownRemaining) : 'unknown'}`}>
            {safety ? formatCooldown(cooldownRemaining) : '—'}
          </span>
          <WriteModeBadge safety={safety} />
          <button
            type="button"
            className="icon-btn"
            onClick={onRefreshCookies}
            disabled={isRefreshing}
            aria-label="Sync Chrome session"
          >
            <RefreshCw size={16} className={isRefreshing ? 'spin' : ''} />
          </button>
        </div>
      </header>

      <nav className="mobile-nav" aria-label="Main navigation">
        {NAV_ITEMS.map(({ id, short, icon: Icon }) => (
          <button
            key={id}
            type="button"
            className="mobile-nav-btn"
            aria-current={activeTab === id ? 'page' : undefined}
            onClick={() => setActiveTab(id)}
          >
            <Icon size={20} aria-hidden="true" />
            {short}
          </button>
        ))}
      </nav>
    </>
  );
};
