import React, { useState } from 'react';
import { ScheduledPost } from '../types';

interface CalendarViewProps {
  posts: ScheduledPost[];
  onSelectPost: (post: ScheduledPost) => void;
  onPublishPost: (postId: string) => void;
  isPublishing: boolean;
}

export const CalendarView: React.FC<CalendarViewProps> = ({
  posts,
  onSelectPost,
  onPublishPost,
  isPublishing,
}) => {
  const [activePost, setActivePost] = useState<ScheduledPost | null>(null);

  // Group 35 posts by Day (1 to 7)
  const days = [1, 2, 3, 4, 5, 6, 7];
  const dayThemes = [
    'Agentic Coding & Tool Calling',
    'Model Context Protocol (MCP)',
    'AI Code Debt & Guardrails',
    'Vibe Coding & Velocity',
    'Agent Reliability & SRE',
    'Local AI & Small Models',
    'Open-Source Growth & Distribution',
  ];

  const getPostsForDay = (day: number) => {
    return posts.filter((p) => p.day === day).sort((a, b) => a.slot - b.slot);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: 700, fontFamily: 'var(--font-display)' }}>
            7-Day Technical Publishing Matrix
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            35 pre-loaded high-signal engineering updates distributed across 5 global time slots per day.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', fontSize: '12px' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span className="status-badge status-pending">PENDING</span> {posts.filter(p => p.status === 'PENDING').length}
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span className="status-badge status-published">PUBLISHED</span> {posts.filter(p => p.status === 'PUBLISHED').length}
          </span>
        </div>
      </div>

      {/* 7-Column Visual Grid */}
      <div className="calendar-grid">
        {days.map((d) => {
          const dayPosts = getPostsForDay(d);
          return (
            <div key={d} className="day-column">
              <div className="day-header">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="day-name">Day {d}</span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>5 slots</span>
                </div>
                <div className="day-theme">{dayThemes[d - 1]}</div>
              </div>

              {dayPosts.map((post) => (
                <div
                  key={post.id}
                  className="slot-card"
                  onClick={() => {
                    setActivePost(post);
                    onSelectPost(post);
                  }}
                  style={{
                    borderLeft: post.status === 'PUBLISHED' ? '3px solid var(--accent-green)' : '3px solid var(--accent-amber)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span className="slot-time">{post.time_utc}</span>
                    <span style={{ fontSize: '10px', background: 'rgba(56, 189, 248, 0.1)', color: 'var(--accent-cyan)', padding: '1px 5px', borderRadius: '4px', fontWeight: 600 }}>
                      {post.hook_formula}
                    </span>
                  </div>

                  <div className="slot-title">{post.title}</div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '6px' }}>
                    <span className={`status-badge ${post.status === 'PUBLISHED' ? 'status-published' : 'status-pending'}`}>
                      {post.status}
                    </span>

                    <button
                      type="button"
                      className="btn-secondary"
                      style={{ padding: '2px 8px', fontSize: '10px' }}
                      onClick={(e) => {
                        e.stopPropagation();
                        onPublishPost(post.id);
                      }}
                      disabled={isPublishing}
                    >
                      Post
                    </button>
                  </div>
                </div>
              ))}
            </div>
          );
        })}
      </div>

      {/* Detail Drawer Modal when post is clicked */}
      {activePost && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
          <div className="glass-panel" style={{ maxWidth: '640px', width: '100%', padding: '24px', background: 'var(--bg-secondary)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <span style={{ fontSize: '12px', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                  Day {activePost.day} • Slot {activePost.slot} ({activePost.time_utc}) • {activePost.theme}
                </span>
                <h3 style={{ fontSize: '18px', fontWeight: 700, marginTop: '4px' }}>{activePost.title}</h3>
              </div>
              <button
                type="button"
                onClick={() => setActivePost(null)}
                style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: '18px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)', padding: '14px', fontSize: '14px', lineHeight: 1.6, whiteSpace: 'pre-wrap', maxHeight: '300px', overflowY: 'auto', marginBottom: '16px' }}>
              {activePost.text}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                Hook: <strong>{activePost.hook_formula}</strong> | Targets: <strong>{activePost.target_platforms.join(', ')}</strong>
              </div>

              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => {
                    onSelectPost(activePost);
                    setActivePost(null);
                  }}
                >
                  Load in Composer
                </button>
                <button
                  type="button"
                  className="btn-primary"
                  onClick={() => {
                    onPublishPost(activePost.id);
                    setActivePost(null);
                  }}
                  disabled={isPublishing}
                >
                  Publish Now
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
