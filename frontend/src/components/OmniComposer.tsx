import React, { useState } from 'react';
import { Check, CircleAlert, CircleCheck, Eye, Paperclip, Send, Sparkles, X } from 'lucide-react';
import { AuditData, HookFormula } from '../types';
import { PLATFORM_IDS, getPlatformMeta } from '../platforms';
import { Modal, PlatformGlyph } from './ui';

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

const scoreTone = (score: number) => (score <= 15 ? 'var(--accent)' : score <= 40 ? 'var(--warning)' : 'var(--danger)');

const SlopGauge: React.FC<{ score: number }> = ({ score }) => {
  const r = 22;
  const c = 2 * Math.PI * r;
  const pct = Math.min(100, Math.max(0, score)) / 100;
  return (
    <div className="gauge" role="img" aria-label={`Slop score ${score} out of 100`}>
      <svg width="52" height="52" viewBox="0 0 52 52">
        <circle cx="26" cy="26" r={r} fill="none" stroke="var(--surface-3)" strokeWidth="4" />
        <circle
          cx="26"
          cy="26"
          r={r}
          fill="none"
          stroke={scoreTone(score)}
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - Math.max(pct, 0.02))}
        />
      </svg>
      <span className="gauge-value" style={{ color: scoreTone(score) }}>
        {score}
      </span>
    </div>
  );
};

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

  const wordCount = text.split(/\s+/).filter(Boolean).length;
  const readSeconds = Math.max(1, Math.ceil(wordCount / 3.5));
  const score = auditData?.slop_score ?? 0;
  const flags = auditData?.flagged_terms ?? [];
  const canSubmit = !isPublishing && text.trim().length > 0 && selectedPlatforms.length > 0;

  const togglePlatform = (p: string) => {
    setSelectedPlatforms((prev) => (prev.includes(p) ? prev.filter((item) => item !== p) : [...prev, p]));
  };

  const handleHookSelect = (hookId: string) => {
    const selected = availableHooks.find((h) => h.id === hookId);
    if (!selected) return;
    const lines = text.split('\n');
    lines[0] = selected.example;
    setText(lines.join('\n'));
  };

  const handleAddMedia = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!mediaInput.trim()) return;
    setMediaPaths((prev) => [...prev, mediaInput.trim()]);
    setMediaInput('');
  };

  const handleRemoveMedia = (idx: number) => {
    setMediaPaths((prev) => prev.filter((_, i) => i !== idx));
  };

  const applySuggestion = (phrase: string, suggestion: string) => {
    const firstSug = suggestion.split(',')[0].trim();
    if (phrase === 'Staccato Bullet Stack') return;
    const escaped = phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`\\b${escaped}\\b`, 'i');
    setText(text.replace(regex, firstSug));
  };

  return (
    <section className="card" aria-label="Composer">
      <div className="toolbar">
        <div className="toolbar-row">
          <span className="toolbar-label" id="targets-label">
            Publish to
          </span>
          <div className="row" style={{ minWidth: 0 }}>
            <label htmlFor="hook-formula-select" className="sr-only">
              Hook template
            </label>
            <select
              id="hook-formula-select"
              className="select"
              style={{ minHeight: 32, fontSize: 12.5, width: 'auto', maxWidth: 240 }}
              onChange={(e) => handleHookSelect(e.target.value)}
              defaultValue=""
            >
              <option value="" disabled>
                Insert hook template…
              </option>
              {availableHooks.map((h) => (
                <option key={h.id} value={h.id}>
                  {h.id} · {h.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="chip-group" role="group" aria-labelledby="targets-label">
          {PLATFORM_IDS.map((p) => {
            const active = selectedPlatforms.includes(p);
            return (
              <button key={p} type="button" className="chip" aria-pressed={active} onClick={() => togglePlatform(p)}>
                <PlatformGlyph id={p} />
                {getPlatformMeta(p).label}
                {active && (
                  <span className="chip-check" aria-hidden="true">
                    <Check size={14} strokeWidth={2.5} />
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {selectedPlatforms.includes('wordpress') && (
        <>
          <label htmlFor="composer-title-input" className="sr-only">
            Article title for WordPress
          </label>
          <input
            id="composer-title-input"
            type="text"
            className="title-input"
            placeholder="Article title (WordPress)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </>
      )}

      <label htmlFor="composer-textarea" className="sr-only">
        Post content
      </label>
      <textarea
        id="composer-textarea"
        className="editor"
        placeholder="Write your master update. Links move to LinkedIn's first comment automatically; long text splits into an X thread."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <div className="editor-meta">
        <div className="editor-meta-stats">
          <span>
            <b>{text.length}</b> chars
          </span>
          <span>
            <b>{wordCount}</b> words
          </span>
          <span>
            ~<b>{readSeconds}s</b> read
          </span>
        </div>
        {auditData?.hook_detected && (
          <span className="badge badge-info">
            <Sparkles size={12} aria-hidden="true" />
            {auditData.hook_detected.formula_id} · {auditData.hook_detected.formula_name}
          </span>
        )}
      </div>

      <div className="radar" id="slop-radar-meter">
        <div className="radar-summary">
          <SlopGauge score={score} />
          <div style={{ minWidth: 0 }}>
            <div className="row" style={{ gap: 8 }}>
              <span style={{ fontWeight: 600, fontSize: 13.5 }}>Slop Radar</span>
              <span className={`badge ${score <= 15 ? 'badge-ok' : score <= 40 ? 'badge-warn' : 'badge-danger'}`}>
                {auditData ? auditData.slop_rating : 'Idle'}
              </span>
            </div>
            <p className="muted" style={{ fontSize: 12.5, marginTop: 2 }}>
              {!auditData
                ? 'Start typing to analyze tone.'
                : flags.length === 0
                  ? 'No synthetic tropes detected. Reads human.'
                  : `${flags.length} synthetic phrase${flags.length > 1 ? 's' : ''} flagged — click to replace.`}
            </p>
          </div>
        </div>

        {flags.length > 0 && (
          <div className="flag-list">
            {flags.map((flag, idx) => (
              <button
                key={`${flag.phrase}-${idx}`}
                type="button"
                className="flag"
                onClick={() => applySuggestion(flag.phrase, flag.suggestion)}
                title={`Replace with: ${flag.suggestion}`}
              >
                <span>{`"${flag.phrase}"`}</span>
                <span className="flag-suggestion" aria-hidden="true">
                  {'→'} {flag.suggestion.split(',')[0]}
                </span>
                <span className="sr-only">, replace with {flag.suggestion.split(',')[0]}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="media-panel">
        <div className="row" style={{ justifyContent: 'space-between' }}>
          <span className="label">Media attachments</span>
          <span className="hint">
            {mediaPaths.length > 0 ? `${mediaPaths.length} attached · browser engine` : 'Uses Tier 2 browser engine'}
          </span>
        </div>
        <form className="inline-form" onSubmit={handleAddMedia}>
          <label htmlFor="media-path-input" className="sr-only">
            Local image path
          </label>
          <input
            id="media-path-input"
            type="text"
            className="input"
            placeholder="/Users/you/screenshot.png"
            value={mediaInput}
            onChange={(e) => setMediaInput(e.target.value)}
          />
          <button type="submit" className="btn btn-secondary" disabled={!mediaInput.trim()}>
            <Paperclip size={14} aria-hidden="true" />
            Attach
          </button>
        </form>
        {mediaPaths.length > 0 && (
          <div className="chip-group">
            {mediaPaths.map((p, i) => (
              <span key={`${p}-${i}`} className="file-chip">
                <span>{p.split('/').pop()}</span>
                <button type="button" onClick={() => handleRemoveMedia(i)} aria-label={`Remove ${p.split('/').pop()}`}>
                  <X size={12} />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {publishResult && (
        <div style={{ padding: '0 18px 16px' }}>
          <div className={`callout ${publishResult.successful_targets > 0 ? 'callout-ok' : 'callout-warn'}`} role="status">
            {publishResult.successful_targets > 0 ? <CircleCheck size={16} /> : <CircleAlert size={16} />}
            <div>
              <div className="callout-title">{publishResult.dry_run ? 'Dry-run complete' : 'Broadcast result'}</div>
              <div>
                {publishResult.successful_targets}/{publishResult.total_targets} targets succeeded in{' '}
                <span className="mono">{publishResult.elapsed_ms}ms</span>.
              </div>
              {publishResult.write_gate_note && (
                <div className="text-warn" style={{ marginTop: 4 }}>
                  {publishResult.write_gate_note}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="card-footer">
        <span className="hint">
          {selectedPlatforms.length === 0
            ? 'Select at least one channel.'
            : `${selectedPlatforms.length} channel${selectedPlatforms.length > 1 ? 's' : ''} selected`}
        </span>
        <div className="composer-actions">
          <button
            id="btn-preview-dryrun"
            type="button"
            className="btn btn-secondary"
            onClick={() => onBroadcast(false, true)}
            disabled={!canSubmit}
          >
            <Eye size={15} aria-hidden="true" />
            Dry run
          </button>
          <button
            id="btn-broadcast-live"
            type="button"
            className="btn btn-primary"
            onClick={() => setShowConfirmModal(true)}
            disabled={!canSubmit}
          >
            <Send size={15} aria-hidden="true" />
            {isPublishing ? 'Broadcasting…' : 'Broadcast'}
          </button>
        </div>
      </div>

      <Modal
        open={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        title="Confirm broadcast"
        description="This will publish live to every selected channel."
        footer={
          <>
            <button type="button" className="btn btn-secondary" onClick={() => setShowConfirmModal(false)}>
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => {
                setShowConfirmModal(false);
                onBroadcast(true, false);
              }}
            >
              <Send size={15} aria-hidden="true" />
              Authorize & post
            </button>
          </>
        }
      >
        <div className="chip-group">
          {selectedPlatforms.map((p) => (
            <span key={p} className="badge" style={{ height: 28, paddingLeft: 4 }}>
              <PlatformGlyph id={p} />
              {getPlatformMeta(p).label}
            </span>
          ))}
        </div>
        <div className="callout callout-info">
          <CircleAlert size={16} />
          <div>
            {mediaPaths.length > 0
              ? 'Media attached — executes via the Patchright browser engine.'
              : 'Text-only — executes via the sub-second Voyager REST API.'}{' '}
            The anti-ban guard enforces a 3-minute cooldown afterwards.
          </div>
        </div>
      </Modal>
    </section>
  );
};
