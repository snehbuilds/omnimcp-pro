import React, { useState } from 'react';
import {
  ChartNoAxesColumn,
  Check,
  Globe,
  Heart,
  ImageIcon,
  Link2,
  MessageCircle,
  Monitor,
  Repeat2,
  Send,
  ThumbsUp,
} from 'lucide-react';
import { TransformedPlatform } from '../types';
import { PLATFORM_IDS, getPlatformMeta } from '../platforms';
import { PlatformGlyph } from './ui';

interface PlatformPreviewProps {
  transformed: Record<string, TransformedPlatform>;
  selectedPlatforms: string[];
  mediaPaths: string[];
}

const FOLD = 180;

const MediaPlaceholder: React.FC<{ count: number }> = ({ count }) =>
  count > 0 ? (
    <div className="media-placeholder">
      <ImageIcon size={16} aria-hidden="true" />
      {count} media attachment{count > 1 ? 's' : ''}
    </div>
  ) : null;

export const PlatformPreview: React.FC<PlatformPreviewProps> = ({ transformed, selectedPlatforms, mediaPaths }) => {
  const [activePlatformTab, setActivePlatformTab] = useState<string>('linkedin');
  const [isLinkedInFoldOpen, setIsLinkedInFoldOpen] = useState(false);

  const current: TransformedPlatform = transformed[activePlatformTab] || {
    platform: activePlatformTab,
    body: 'Start writing in the composer to see a live, platform-native preview here.',
    character_count: 0,
    warnings: [],
  };

  const body = current.body || '';

  return (
    <section className="card preview-sticky" aria-label="Live platform preview">
      <div className="card-header">
        <div>
          <h2 className="card-title">
            <Monitor size={16} aria-hidden="true" />
            Live preview
          </h2>
          <p className="card-subtitle">Rendered exactly as each network formats it.</p>
        </div>
      </div>

      <div style={{ padding: '12px 18px', borderBottom: '1px solid var(--border)' }}>
        <div className="segmented" role="tablist" aria-label="Preview platform">
          {PLATFORM_IDS.map((p) => (
            <button
              key={p}
              type="button"
              role="tab"
              className="segment"
              aria-selected={activePlatformTab === p}
              onClick={() => setActivePlatformTab(p)}
            >
              {selectedPlatforms.includes(p) && <span className="segment-dot" aria-label="selected target" />}
              {getPlatformMeta(p).short}
            </button>
          ))}
        </div>
      </div>

      <div className="preview-stage" role="tabpanel">
        {current.warnings && current.warnings.length > 0 && (
          <ul className="callout callout-ok" style={{ listStyle: 'none', flexDirection: 'column', gap: 4 }}>
            {current.warnings.map((w, i) => (
              <li key={i} className="row" style={{ alignItems: 'flex-start' }}>
                <Check size={14} aria-hidden="true" style={{ color: 'var(--accent)', marginTop: 3 }} />
                <span>{w}</span>
              </li>
            ))}
          </ul>
        )}

        {activePlatformTab === 'linkedin' && (
          <article className="post">
            <div className="post-author">
              <PlatformGlyph id="linkedin" size="lg" />
              <div>
                <div className="post-author-name">OmniMCP Pro Creator</div>
                <div className="post-author-meta">Protocol-Native Systems Engineer</div>
                <div className="post-author-meta">
                  Just now · <Globe size={11} aria-label="Public" />
                </div>
              </div>
            </div>
            <div className="post-body">
              {isLinkedInFoldOpen || body.length <= FOLD ? body : `${body.slice(0, FOLD)}…`}
              {body.length > FOLD && (
                <button type="button" className="link-btn" onClick={() => setIsLinkedInFoldOpen(!isLinkedInFoldOpen)}>
                  {isLinkedInFoldOpen ? ' show less' : ' see more'}
                </button>
              )}
            </div>
            <MediaPlaceholder count={mediaPaths.length} />
            <div className="post-actions" aria-hidden="true">
              <span>
                <ThumbsUp size={14} /> Like
              </span>
              <span>
                <MessageCircle size={14} /> Comment
              </span>
              <span>
                <Repeat2 size={14} /> Repost
              </span>
              <span>
                <Send size={14} /> Send
              </span>
            </div>
            {current.first_comment && (
              <div style={{ marginTop: 14 }}>
                <div className="row hint" style={{ marginBottom: 6, gap: 6 }}>
                  <Link2 size={12} aria-hidden="true" />
                  Pinned first comment — link moved here to protect reach
                </div>
                <div className="readout" style={{ padding: '10px 12px', fontSize: 13 }}>
                  {current.first_comment}
                </div>
              </div>
            )}
          </article>
        )}

        {activePlatformTab === 'twitter' && (
          <div className="thread">
            {(current.thread_items && current.thread_items.length > 0 ? current.thread_items : [body]).map((tweet, idx, all) => (
              <article key={idx} className="post">
                <div className="post-author" style={{ marginBottom: 8 }}>
                  <PlatformGlyph id="twitter" size="lg" />
                  <div style={{ minWidth: 0 }}>
                    <div className="post-author-name">OmniMCP Pro</div>
                    <div className="post-author-meta">
                      @omnimcp_pro{all.length > 1 ? ` · ${idx + 1}/${all.length}` : ''}
                    </div>
                  </div>
                  <span className={`char-count ${tweet.length > 280 ? 'over' : ''}`}>{tweet.length}/280</span>
                </div>
                <div className="post-body">{tweet}</div>
                {idx === 0 && <MediaPlaceholder count={mediaPaths.length} />}
                <div className="post-actions" aria-hidden="true">
                  <span>
                    <MessageCircle size={14} /> 12
                  </span>
                  <span>
                    <Repeat2 size={14} /> 48
                  </span>
                  <span>
                    <Heart size={14} /> 215
                  </span>
                  <span>
                    <ChartNoAxesColumn size={14} /> 4.2k
                  </span>
                </div>
              </article>
            ))}
          </div>
        )}

        {activePlatformTab === 'wordpress' && (
          <article className="post wp-article" style={{ padding: 20 }}>
            <span className="badge badge-info" style={{ marginBottom: 12 }}>
              WordPress REST render
            </span>
            <h2>{current.metadata?.title || 'Untitled post'}</h2>
            <div className="wp-content" dangerouslySetInnerHTML={{ __html: current.html_body || '<p>No content yet.</p>' }} />
          </article>
        )}

        {activePlatformTab === 'threads' && (
          <article className="post">
            <div className="post-author">
              <PlatformGlyph id="threads" size="lg" />
              <div>
                <div className="post-author-name">omnimcp.pro</div>
                <div className="post-author-meta">Just now</div>
              </div>
              <span className={`char-count ${current.character_count > 500 ? 'over' : ''}`}>
                {current.character_count}/500
              </span>
            </div>
            <div className="post-body">{body}</div>
            <MediaPlaceholder count={mediaPaths.length} />
          </article>
        )}

        {activePlatformTab === 'facebook' && (
          <article className="post">
            <div className="post-author">
              <PlatformGlyph id="facebook" size="lg" />
              <div>
                <div className="post-author-name">OmniMCP Pro</div>
                <div className="post-author-meta">
                  Just now · <Globe size={11} aria-label="Public" />
                </div>
              </div>
            </div>
            <div className="post-body">{body}</div>
            <MediaPlaceholder count={mediaPaths.length} />
            <div className="post-actions" aria-hidden="true">
              <span>
                <ThumbsUp size={14} /> Like
              </span>
              <span>
                <MessageCircle size={14} /> Comment
              </span>
              <span>
                <Send size={14} /> Share
              </span>
            </div>
          </article>
        )}
      </div>
    </section>
  );
};
