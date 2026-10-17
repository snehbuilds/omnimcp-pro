import React, { useMemo, useState } from 'react';
import { CalendarDays, CircleCheck, Clock, PenLine, Send, CircleAlert } from 'lucide-react';
import { ScheduledPost } from '../types';
import { Modal, PageHeader, PlatformGlyph } from './ui';

interface CalendarViewProps {
  posts: ScheduledPost[];
  onSelectPost: (post: ScheduledPost) => void;
  onPublishPost: (postId: string) => void;
  isPublishing: boolean;
}

const DAY_THEMES = [
  'Agentic Coding & Tool Calling',
  'Model Context Protocol (MCP)',
  'AI Code Debt & Guardrails',
  'Vibe Coding & Velocity',
  'Agent Reliability & SRE',
  'Local AI & Small Models',
  'Open-Source Growth & Distribution',
];

const statusBadge = (status: ScheduledPost['status']) => {
  switch (status) {
    case 'PUBLISHED':
      return 'badge-ok';
    case 'FAILED':
      return 'badge-danger';
    case 'SKIPPED':
      return '';
    default:
      return 'badge-warn';
  }
};

const statusLabel = (status: ScheduledPost['status']) => status.charAt(0) + status.slice(1).toLowerCase();

export const CalendarView: React.FC<CalendarViewProps> = ({ posts, onSelectPost, onPublishPost, isPublishing }) => {
  const [activePost, setActivePost] = useState<ScheduledPost | null>(null);

  const byDay = useMemo(() => {
    const map = new Map<number, ScheduledPost[]>();
    for (let d = 1; d <= 7; d++) map.set(d, []);
    posts.forEach((p) => map.get(p.day)?.push(p));
    map.forEach((list) => list.sort((a, b) => a.slot - b.slot));
    return map;
  }, [posts]);

  const pending = posts.filter((p) => p.status === 'PENDING').length;
  const published = posts.filter((p) => p.status === 'PUBLISHED').length;
  const failed = posts.filter((p) => p.status === 'FAILED').length;
  const progress = posts.length ? Math.round((published / posts.length) * 100) : 0;

  return (
    <>
      <PageHeader
        eyebrow={
          <>
            <CalendarDays size={13} aria-hidden="true" /> Publishing matrix
          </>
        }
        title="7-day calendar"
        description="35 high-signal engineering updates distributed across five global time slots per day."
      />

      <div className="stat-strip">
        <div>
          <div className="stat-label">Scheduled</div>
          <div className="stat-value">{posts.length}</div>
        </div>
        <div>
          <div className="stat-label">
            <span className="dot dot-warn" aria-hidden="true" /> Pending
          </div>
          <div className="stat-value">{pending}</div>
        </div>
        <div>
          <div className="stat-label">
            <span className="dot dot-ok" aria-hidden="true" /> Published
          </div>
          <div className="stat-value">{published}</div>
        </div>
        <div>
          <div className="stat-label">Progress</div>
          <div className="stat-value">
            {progress}%{failed > 0 && <span className="badge badge-danger" style={{ marginLeft: 8, verticalAlign: 'middle' }}>{failed} failed</span>}
          </div>
        </div>
      </div>

      {posts.length === 0 ? (
        <div className="empty">
          <span className="empty-icon">
            <CalendarDays size={20} aria-hidden="true" />
          </span>
          <div className="empty-title">No scheduled posts yet</div>
          <p>Connect the backend scheduler to load the 35-post publishing matrix. Posts appear here grouped by day.</p>
        </div>
      ) : (
        <div className="board" role="list" aria-label="Days">
          {DAY_THEMES.map((theme, i) => {
            const day = i + 1;
            const dayPosts = byDay.get(day) ?? [];
            const done = dayPosts.filter((p) => p.status === 'PUBLISHED').length;
            return (
              <section key={day} className="board-column" role="listitem" aria-label={`Day ${day}`}>
                <div className="board-column-header">
                  <div className="board-column-title">
                    <span>Day {day}</span>
                    <span className="badge badge-mono">
                      {done}/{dayPosts.length || 5}
                    </span>
                  </div>
                  <div className="board-column-theme">{theme}</div>
                </div>
                {dayPosts.map((post) => (
                  <button key={post.id} type="button" className="slot" onClick={() => setActivePost(post)}>
                    <div className="slot-top">
                      <span className="row" style={{ gap: 5 }}>
                        <Clock size={11} aria-hidden="true" />
                        {post.time_utc}
                      </span>
                      <span>{post.hook_formula}</span>
                    </div>
                    <div className="slot-title">{post.title}</div>
                    <div className="row" style={{ justifyContent: 'space-between' }}>
                      <span className={`badge ${statusBadge(post.status)}`}>{statusLabel(post.status)}</span>
                      <span className="row" style={{ gap: 3 }}>
                        {post.target_platforms.slice(0, 3).map((p) => (
                          <PlatformGlyph key={p} id={p} />
                        ))}
                      </span>
                    </div>
                  </button>
                ))}
              </section>
            );
          })}
        </div>
      )}

      <Modal
        open={!!activePost}
        onClose={() => setActivePost(null)}
        width={640}
        title={activePost?.title ?? ''}
        description={
          activePost && (
            <span className="mono" style={{ fontSize: 12 }}>
              Day {activePost.day} · Slot {activePost.slot} · {activePost.time_utc} UTC · {activePost.theme}
            </span>
          )
        }
        footer={
          activePost && (
            <>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  onSelectPost(activePost);
                  setActivePost(null);
                }}
              >
                <PenLine size={15} aria-hidden="true" />
                Open in composer
              </button>
              <button
                type="button"
                className="btn btn-primary"
                disabled={isPublishing || activePost.status === 'PUBLISHED'}
                onClick={() => {
                  onPublishPost(activePost.id);
                  setActivePost(null);
                }}
              >
                <Send size={15} aria-hidden="true" />
                {activePost.status === 'PUBLISHED' ? 'Already published' : 'Publish now'}
              </button>
            </>
          )
        }
      >
        {activePost && (
          <>
            <div className="kv">
              <span className={`badge ${statusBadge(activePost.status)}`}>
                {activePost.status === 'PUBLISHED' ? <CircleCheck size={12} /> : activePost.status === 'FAILED' ? <CircleAlert size={12} /> : <Clock size={12} />}
                {statusLabel(activePost.status)}
              </span>
              <span className="badge badge-info badge-mono">{activePost.hook_formula}</span>
              {activePost.target_platforms.map((p) => (
                <span key={p} className="badge" style={{ paddingLeft: 3 }}>
                  <PlatformGlyph id={p} />
                  <span style={{ textTransform: 'capitalize' }}>{p}</span>
                </span>
              ))}
            </div>
            <div className="readout">{activePost.text}</div>
          </>
        )}
      </Modal>
    </>
  );
};
