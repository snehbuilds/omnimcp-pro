import React, { useState } from 'react';
import { TransformedPlatform } from '../types';

interface PlatformPreviewProps {
  transformed: Record<string, TransformedPlatform>;
  selectedPlatforms: string[];
  mediaPaths: string[];
}

export const PlatformPreview: React.FC<PlatformPreviewProps> = ({
  transformed,
  selectedPlatforms,
  mediaPaths,
}) => {
  const [activePlatformTab, setActivePlatformTab] = useState<string>('linkedin');
  const [isLinkedInFoldOpen, setIsLinkedInFoldOpen] = useState(false);

  const currentTransformed = transformed[activePlatformTab] || {
    platform: activePlatformTab,
    body: 'Enter content in the composer to view real-time platform previews.',
    character_count: 0,
    warnings: [],
  };

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      {/* Header and Platform selection tabs */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, fontFamily: 'var(--font-display)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
            <line x1="8" y1="21" x2="16" y2="21"></line>
            <line x1="12" y1="17" x2="12" y2="21"></line>
          </svg>
          Live Platform Preview
        </h3>

        <div className="platform-preview-tabs" style={{ border: 'none', margin: 0, padding: 0 }}>
          {['linkedin', 'twitter', 'wordpress', 'threads', 'facebook'].map((p) => {
            const isTarget = selectedPlatforms.includes(p);
            return (
              <button
                key={p}
                className={`platform-btn ${activePlatformTab === p ? 'active' : ''}`}
                onClick={() => setActivePlatformTab(p)}
                style={{
                  opacity: isTarget ? 1 : 0.6,
                  borderColor: activePlatformTab === p ? 'var(--accent-cyan)' : 'var(--border-subtle)',
                }}
              >
                <span style={{ textTransform: 'capitalize' }}>{p === 'wordpress' ? 'WP' : p === 'twitter' ? 'X' : p}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Warnings & Algorithmic Optimizations Banner */}
      {currentTransformed.warnings && currentTransformed.warnings.length > 0 && (
        <div style={{ background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.25)', borderRadius: 'var(--radius-sm)', padding: '8px 12px', marginBottom: '16px', fontSize: '12px', color: 'var(--accent-cyan)' }}>
          {currentTransformed.warnings.map((w, i) => (
            <div key={i}>✓ {w}</div>
          ))}
        </div>
      )}

      {/* LINKEDIN PREVIEW CARD */}
      {activePlatformTab === 'linkedin' && (
        <div style={{ background: '#1b1f2b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
          {/* Author Header */}
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '12px' }}>
            <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'linear-gradient(135deg, #0a66c2, #38bdf8)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '18px', color: '#fff' }}>
              OM
            </div>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#fff' }}>OmniMCP Pro Creator</div>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>Protocol-Native Social Systems Engineer</div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>Just now • 🌐</div>
            </div>
          </div>

          {/* Post Text with fold cutoff */}
          <div style={{ fontSize: '14px', lineHeight: 1.6, color: '#f1f5f9', whiteSpace: 'pre-wrap', marginBottom: '12px' }}>
            {isLinkedInFoldOpen
              ? currentTransformed.body
              : currentTransformed.body.slice(0, 180) + (currentTransformed.body.length > 180 ? '...' : '')}
            {currentTransformed.body.length > 180 && (
              <button
                type="button"
                onClick={() => setIsLinkedInFoldOpen(!isLinkedInFoldOpen)}
                style={{ background: 'transparent', border: 'none', color: '#38bdf8', cursor: 'pointer', fontWeight: 600, marginLeft: '4px' }}
              >
                {isLinkedInFoldOpen ? 'Show less' : '...see more'}
              </button>
            )}
          </div>

          {/* Media preview */}
          {mediaPaths.length > 0 && (
            <div style={{ background: '#111420', border: '1px dashed var(--border-medium)', borderRadius: 'var(--radius-sm)', padding: '30px', textAlign: 'center', marginBottom: '12px', color: 'var(--text-muted)', fontSize: '13px' }}>
              🖼️ [{mediaPaths.length} Media Attachment(s) Loaded]
            </div>
          )}

          {/* LinkedIn Engagement Footer */}
          <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '10px', fontSize: '12px', color: '#94a3b8' }}>
            <span>👍 Like</span>
            <span>💬 Comment</span>
            <span>🔁 Repost</span>
            <span>↗ Send</span>
          </div>

          {/* Algorithmic First-Comment Link Drop */}
          {currentTransformed.first_comment && (
            <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px dashed rgba(255,255,255,0.1)' }}>
              <div style={{ fontSize: '11px', color: 'var(--accent-cyan)', fontWeight: 600, marginBottom: '6px' }}>
                🔗 Pinned 1st Comment (Link dropped here to protect feed reach):
              </div>
              <div style={{ background: '#121624', borderRadius: 'var(--radius-md)', padding: '10px 14px', fontSize: '13px', color: '#f8fafc' }}>
                {currentTransformed.first_comment}
              </div>
            </div>
          )}
        </div>
      )}

      {/* X (TWITTER) THREAD PREVIEW */}
      {activePlatformTab === 'twitter' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {(currentTransformed.thread_items || [currentTransformed.body]).map((tweet, idx) => (
            <div
              key={idx}
              style={{
                background: '#15202b',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 'var(--radius-md)',
                padding: '16px',
                position: 'relative',
              }}
            >
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '8px' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: '#1d9bf0', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '14px', color: '#fff' }}>
                  X
                </div>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 700, color: '#fff' }}>OmniMCP Pro <span style={{ color: '#8899a6', fontWeight: 400 }}>@omnimcp_pro</span></div>
                </div>
                <div style={{ marginLeft: 'auto', fontSize: '11px', color: tweet.length > 280 ? 'var(--accent-rose)' : 'var(--text-muted)' }}>
                  {tweet.length}/280
                </div>
              </div>

              <div style={{ fontSize: '14px', lineHeight: 1.5, color: '#fff', whiteSpace: 'pre-wrap' }}>
                {tweet}
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid rgba(255,255,255,0.06)', marginTop: '12px', paddingTop: '8px', fontSize: '12px', color: '#8899a6' }}>
                <span>💬 12</span>
                <span>🔁 48</span>
                <span>❤️ 215</span>
                <span>📊 4.2k</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* WORDPRESS SEMANTIC HTML PREVIEW */}
      {activePlatformTab === 'wordpress' && (
        <div style={{ background: '#141824', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 'var(--radius-md)', padding: '20px' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-wordpress)', textTransform: 'uppercase', fontWeight: 700, marginBottom: '4px' }}>
            WordPress REST Rendered Preview
          </div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#fff', marginBottom: '14px' }}>
            {currentTransformed.metadata?.title || 'Untitled Post'}
          </h2>
          <div
            style={{ fontSize: '14px', lineHeight: 1.7, color: '#cbd5e1' }}
            dangerouslySetInnerHTML={{ __html: currentTransformed.html_body || '<p>No content</p>' }}
          />
        </div>
      )}

      {/* THREADS PREVIEW */}
      {activePlatformTab === 'threads' && (
        <div style={{ background: '#101010', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '10px' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: '#fff', color: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800 }}>
              @
            </div>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#fff' }}>omnimcp.pro</div>
              <div style={{ fontSize: '11px', color: '#777' }}>Threads • 500 max</div>
            </div>
            <div style={{ marginLeft: 'auto', fontSize: '11px', color: 'var(--text-muted)' }}>
              {currentTransformed.character_count}/500
            </div>
          </div>
          <div style={{ fontSize: '14px', lineHeight: 1.6, color: '#eee', whiteSpace: 'pre-wrap' }}>
            {currentTransformed.body}
          </div>
        </div>
      )}

      {/* FACEBOOK PREVIEW */}
      {activePlatformTab === 'facebook' && (
        <div style={{ background: '#18191a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '10px' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: '#1877f2', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, color: '#fff' }}>
              f
            </div>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#e4e6eb' }}>OmniMCP Pro Page</div>
              <div style={{ fontSize: '11px', color: '#b0b3b8' }}>Just now • 🌎</div>
            </div>
          </div>
          <div style={{ fontSize: '14px', lineHeight: 1.6, color: '#e4e6eb', whiteSpace: 'pre-wrap' }}>
            {currentTransformed.body}
          </div>
        </div>
      )}
    </div>
  );
};
