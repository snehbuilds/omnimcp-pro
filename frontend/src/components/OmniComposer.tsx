import React, { useState } from 'react';
import { AuditData, HookFormula } from '../types';

interface OmniComposerProps {
  text: string;
  setText: (t: string) => void;
  title: string;
  setTitle: (t: string) => void;
  selectedPlatforms: string[];
  setSelectedPlatforms: React.Dispatch<React.SetStateAction<string[]>>;
  mediaPaths: string[];
  setMediaPaths: React.Dispatch<React.SetStateAction<string[]>>;
  auditData: AuditData | null;
  availableHooks: HookFormula[];
  onBroadcast: (confirmPost: boolean, dryRun: boolean) => void;
  isPublishing: boolean;
  publishResult: any;
}

export const OmniComposer: React.FC<OmniComposerProps> = ({
  text,
  setText,
  title,
  setTitle,
  selectedPlatforms,
  setSelectedPlatforms,
  mediaPaths,
  setMediaPaths,
  auditData,
  availableHooks,
  onBroadcast,
  isPublishing,
  publishResult,
}) => {
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [mediaInput, setMediaInput] = useState('');

  const togglePlatform = (p: string) => {
    setSelectedPlatforms((prev) =>
      prev.includes(p) ? prev.filter((item) => item !== p) : [...prev, p]
    );
  };

  const handleHookSelect = (hookId: string) => {
    const selected = availableHooks.find((h) => h.id === hookId);
    if (!selected) return;

    // Prepend or replace opening line with formula example
    const lines = text.split('\n');
    lines[0] = selected.example;
    setText(lines.join('\n'));
  };

  const handleAddMedia = () => {
    if (!mediaInput.trim()) return;
    setMediaPaths((prev) => [...prev, mediaInput.trim()]);
    setMediaInput('');
  };

  const handleRemoveMedia = (idx: number) => {
    setMediaPaths((prev) => prev.filter((_, i) => i !== idx));
  };

  const applySuggestion = (_matchIndex: number, phrase: string, suggestion: string) => {
    // Replace first occurrence of flagged phrase with first suggestion
    const firstSug = suggestion.split(',')[0].trim();
    if (phrase === 'Staccato Bullet Stack') return;
    const regex = new RegExp(`\\b${phrase}\\b`, 'i');
    setText(text.replace(regex, firstSug));
  };

  const getScoreBadgeClass = (score: number) => {
    if (score <= 15) return 'badge-pristine';
    if (score <= 40) return 'badge-warning';
    return 'badge-danger';
  };

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      {/* Header controls: Platform toggles & Hook formula picker */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        {/* Platform target checkboxes */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>Targets:</span>
          {['linkedin', 'twitter', 'wordpress', 'threads', 'facebook'].map((p) => {
            const active = selectedPlatforms.includes(p);
            return (
              <button
                key={p}
                type="button"
                className={`platform-btn ${active ? 'active' : ''}`}
                onClick={() => togglePlatform(p)}
                style={{
                  borderColor: active ? 'var(--accent-cyan)' : 'var(--border-subtle)',
                  background: active ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                }}
              >
                <span style={{ textTransform: 'capitalize' }}>{p === 'wordpress' ? 'WordPress' : p === 'twitter' ? 'X (Twitter)' : p}</span>
              </button>
            );
          })}
        </div>

        {/* Hook Formula Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label htmlFor="hook-formula-select" style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Hook Template:</label>
          <select
            id="hook-formula-select"
            className="btn-secondary"
            style={{ padding: '6px 10px', fontSize: '12px', background: 'var(--bg-secondary)' }}
            onChange={(e) => handleHookSelect(e.target.value)}
            defaultValue=""
          >
            <option value="" disabled>Choose Hook (F01–F20)...</option>
            {availableHooks.map((h) => (
              <option key={h.id} value={h.id}>
                {h.id}: {h.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* WordPress Title input if WP is selected */}
      {selectedPlatforms.includes('wordpress') && (
        <div style={{ marginBottom: '14px' }}>
          <input
            id="composer-title-input"
            type="text"
            className="composer-textarea"
            style={{ minHeight: 'auto', padding: '10px 14px', fontSize: '15px', fontWeight: 600 }}
            placeholder="Article Title (for WordPress)..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>
      )}

      {/* Master Content Textarea */}
      <textarea
        id="composer-textarea"
        className="composer-textarea"
        placeholder="Write your master technical update... (URLs will automatically be moved to LinkedIn first-comment to maximize algorithmic reach; long text will be split into an X thread)."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      {/* Text Metrics Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
        <div style={{ display: 'flex', gap: '16px' }}>
          <span><strong>{text.length}</strong> characters</span>
          <span><strong>{text.split(/\s+/).filter(Boolean).length}</strong> words</span>
          <span>~<strong>{Math.max(1, Math.ceil(text.split(/\s+/).filter(Boolean).length / 3.5))}s</strong> read</span>
        </div>

        {auditData?.hook_detected && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-cyan)' }}>
            <span style={{ fontSize: '11px', textTransform: 'uppercase', fontWeight: 600 }}>Hook:</span>
            <span>{auditData.hook_detected.formula_id} — {auditData.hook_detected.formula_name}</span>
          </div>
        )}
      </div>

      {/* Live AI-Slop Radar Panel */}
      <div className="slop-meter-container" id="slop-radar-meter">
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div className={`slop-score-badge ${getScoreBadgeClass(auditData?.slop_score || 0)}`}>
            {auditData ? auditData.slop_score : 0}
            <span>/100</span>
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
              {auditData ? auditData.slop_rating : 'Slop Radar Inactive'}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              {auditData?.slop_score === 0
                ? 'Zero synthetic tropes detected. Clean human tone.'
                : `${auditData?.flagged_terms.length || 0} synthetic AI phrase(s) flagged`}
            </div>
          </div>
        </div>

        {/* Flagged Phrases Pill list with one-click replace */}
        {auditData && auditData.flagged_terms.length > 0 && (
          <div style={{ flex: 1, display: 'flex', flexWrap: 'wrap', gap: '6px', marginLeft: '16px' }}>
            {auditData.flagged_terms.map((flag, idx) => (
              <span
                key={idx}
                style={{
                  background: 'rgba(244, 63, 94, 0.12)',
                  border: '1px solid rgba(244, 63, 94, 0.3)',
                  color: 'var(--accent-rose)',
                  fontSize: '11px',
                  padding: '3px 8px',
                  borderRadius: 'var(--radius-sm)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  cursor: 'pointer',
                }}
                onClick={() => applySuggestion(flag.index, flag.phrase, flag.suggestion)}
                title={`Suggestion: ${flag.suggestion} (Click to auto-replace)`}
              >
                <span>✕ "{flag.phrase}"</span>
                <span style={{ color: 'var(--text-muted)', fontSize: '10px' }}>→ {flag.suggestion.split(',')[0]}</span>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Media Attachment Management */}
      <div style={{ marginTop: '16px', background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '12px 16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)' }}>Media Attachments (Triggers Tier 2 Patchright Browser):</span>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{mediaPaths.length} file(s) attached</span>
        </div>

        <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
          <input
            id="media-path-input"
            type="text"
            className="composer-textarea"
            style={{ minHeight: 'auto', padding: '6px 12px', fontSize: '13px' }}
            placeholder="Local image path (e.g. /Users/name/screenshot.png or relative path)..."
            value={mediaInput}
            onChange={(e) => setMediaInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAddMedia()}
          />
          <button type="button" className="btn-secondary" onClick={handleAddMedia} style={{ padding: '6px 14px', fontSize: '12px' }}>
            Attach
          </button>
        </div>

        {mediaPaths.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {mediaPaths.map((p, i) => (
              <span
                key={i}
                style={{
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-medium)',
                  padding: '3px 8px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '11px',
                  fontFamily: 'var(--font-mono)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <span>{p.split('/').pop()}</span>
                <button
                  type="button"
                  onClick={() => handleRemoveMedia(i)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--accent-rose)', cursor: 'pointer' }}
                >
                  ✕
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' }}>
        <button
          id="btn-preview-dryrun"
          type="button"
          className="btn-secondary"
          onClick={() => onBroadcast(false, true)}
          disabled={isPublishing || !text.trim()}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
            <circle cx="12" cy="12" r="3"></circle>
          </svg>
          Dry-Run Preview
        </button>

        <button
          id="btn-broadcast-live"
          type="button"
          className="btn-primary"
          onClick={() => setShowConfirmModal(true)}
          disabled={isPublishing || !text.trim()}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
          {isPublishing ? 'Broadcasting...' : 'Broadcast Multi-Platform'}
        </button>
      </div>

      {/* Live Publishing Result Feedback */}
      {publishResult && (
        <div style={{ marginTop: '16px', padding: '12px 16px', background: 'var(--bg-secondary)', border: '1px solid var(--border-medium)', borderRadius: 'var(--radius-md)', fontSize: '13px' }}>
          <div style={{ fontWeight: 600, color: publishResult.successful_targets > 0 ? 'var(--accent-green)' : 'var(--accent-amber)', marginBottom: '4px' }}>
            {publishResult.dry_run ? 'Dry-Run Simulation Complete:' : 'Live Broadcast Result:'}
          </div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
            Targets: {publishResult.successful_targets}/{publishResult.total_targets} succeeded in {publishResult.elapsed_ms}ms.
            {publishResult.write_gate_note && <div style={{ color: 'var(--accent-amber)', marginTop: '4px' }}>Note: {publishResult.write_gate_note}</div>}
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
          <div className="glass-panel" style={{ maxWidth: '480px', width: '100%', padding: '24px', background: 'var(--bg-secondary)' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '12px' }}>Confirm Multi-Platform Broadcast</h3>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '16px', lineHeight: 1.6 }}>
              You are about to publish to <strong>{selectedPlatforms.join(', ')}</strong>.
              {mediaPaths.length > 0 ? ' Media is attached (will execute via Patchright browser).' : ' Text-only (will execute via sub-second Voyager REST API).'}
              <br /><br />
              Anti-Ban Guard will enforce a 3-minute cooldown timer.
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button className="btn-secondary" onClick={() => setShowConfirmModal(false)}>
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={() => {
                  setShowConfirmModal(false);
                  onBroadcast(true, false);
                }}
              >
                Authorize & Post Now
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
