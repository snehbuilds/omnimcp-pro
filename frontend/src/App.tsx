import React, { useState, useEffect, useRef } from 'react';
import { HeaderHUD } from './components/HeaderHUD';
import { OmniComposer } from './components/OmniComposer';
import { PlatformPreview } from './components/PlatformPreview';
import { CalendarView } from './components/CalendarView';
import { AnalyticsView } from './components/AnalyticsView';
import { SettingsView } from './components/SettingsView';
import {
  AuditData,
  HookFormula,
  PlatformStatus,
  SafetyStatus,
  ScheduledPost,
  TransformedPlatform,
} from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'composer' | 'calendar' | 'analytics' | 'settings'>('composer');

  // Composer state
  const [text, setText] = useState<string>(
    'Building in 2024 (custom function-calling schemas) vs 2026 (Model Context Protocol).\n\n' +
    'In 2024: Fragile parsing, prompt-dependent JSON, vendor lock-in.\n' +
    'In 2026: FastMCP protocol gateway connecting Claude, Cursor, and local IDEs over JSON-RPC 2.0.\n\n' +
    'The protocol layer completely won. Full architecture breakdown and open-source implementation:\n' +
    'https://github.com/example/omnimcp-pro'
  );
  const [title, setTitle] = useState<string>('The Protocol-Native Shift in Autonomous Coding');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['linkedin', 'twitter']);
  const [mediaPaths, setMediaPaths] = useState<string[]>([]);

  // Engine state
  const [auditData, setAuditData] = useState<AuditData | null>(null);
  const [availableHooks, setAvailableHooks] = useState<HookFormula[]>([]);
  const [transformed, setTransformed] = useState<Record<string, TransformedPlatform>>({});
  const [safety, setSafety] = useState<SafetyStatus | null>(null);
  const [platforms, setPlatforms] = useState<Record<string, PlatformStatus>>({});
  const [calendarPosts, setCalendarPosts] = useState<ScheduledPost[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);

  // Interaction state
  const [isPublishing, setIsPublishing] = useState<boolean>(false);
  const [isRefreshingCookies, setIsRefreshingCookies] = useState<boolean>(false);
  const [publishResult, setPublishResult] = useState<any>(null);

  const debounceTimerRef = useRef<any>(null);

  // 1. Fetch initial platform & calendar data
  useEffect(() => {
    fetchSafety();
    fetchPlatforms();
    fetchCalendar();
    fetchAnalytics();

    // Setup SSE listener for real-time safety updates
    const eventSource = new EventSource('/api/events');
    eventSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setSafety((prev) => (prev ? { ...prev, ...data } : null));
      } catch (err) {
        // Fallback silently
      }
    };

    return () => {
      eventSource.close();
    };
  }, []);

  // 2. Debounced real-time audit and preview when content changes
  useEffect(() => {
    if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);

    debounceTimerRef.current = setTimeout(() => {
      runAuditAndPreview(text, title, selectedPlatforms, mediaPaths);
    }, 250);

    return () => {
      if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
    };
  }, [text, title, selectedPlatforms, mediaPaths]);

  const fetchSafety = async () => {
    try {
      const res = await fetch('/api/safety');
      if (res.ok) setSafety(await res.json());
    } catch (e) {
      console.error('Failed to fetch safety status', e);
    }
  };

  const fetchPlatforms = async () => {
    try {
      const res = await fetch('/api/platforms');
      if (res.ok) setPlatforms(await res.json());
    } catch (e) {
      console.error('Failed to fetch platforms', e);
    }
  };

  const fetchCalendar = async () => {
    try {
      const res = await fetch('/api/calendar');
      if (res.ok) {
        const data = await res.json();
        setCalendarPosts(data.posts || []);
      }
    } catch (e) {
      console.error('Failed to fetch calendar', e);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const res = await fetch('/api/analytics');
      if (res.ok) setAnalytics(await res.json());
    } catch (e) {
      console.error('Failed to fetch analytics', e);
    }
  };

  const runAuditAndPreview = async (
    currentText: string,
    currentTitle: string,
    targets: string[],
    media: string[]
  ) => {
    try {
      // Run audit
      const auditRes = await fetch('/api/posts/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: currentText }),
      });
      if (auditRes.ok) {
        const data = await auditRes.json();
        setAuditData(data);
        if (data.available_hooks) setAvailableHooks(data.available_hooks);
      }

      // Run live preview
      const previewRes = await fetch('/api/posts/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: currentText,
          title: currentTitle,
          targets: targets,
          media_paths: media,
        }),
      });
      if (previewRes.ok) {
        const pData = await previewRes.json();
        setTransformed(pData.transformed || {});
      }
    } catch (e) {
      console.error('Error during audit or preview', e);
    }
  };

  const handleBroadcast = async (confirmPost: boolean, dryRun: boolean) => {
    setIsPublishing(true);
    setPublishResult(null);

    try {
      const res = await fetch('/api/posts/broadcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          title,
          targets: selectedPlatforms,
          media_paths: mediaPaths,
          confirm_post: confirmPost,
          dry_run: dryRun,
        }),
      });

      const data = await res.json();
      setPublishResult(data);
      fetchSafety();
      fetchCalendar();
    } catch (e) {
      setPublishResult({
        successful_targets: 0,
        total_targets: selectedPlatforms.length,
        elapsed_ms: 0,
        write_gate_note: `Broadcast failed: ${e}`,
      });
    } finally {
      setIsPublishing(false);
    }
  };

  const handlePublishCalendarPost = async (postId: string) => {
    setIsPublishing(true);
    try {
      const res = await fetch(`/api/calendar/${postId}/publish?confirm_post=false`, {
        method: 'POST',
      });
      const data = await res.json();
      setPublishResult(data);
      fetchCalendar();
      fetchSafety();
      setActiveTab('composer');
    } catch (e) {
      alert(`Publish failed: ${e}`);
    } finally {
      setIsPublishing(false);
    }
  };

  const handleRecordMetrics = async (
    postId: string,
    impressions: number,
    reactions: number,
    comments: number
  ) => {
    try {
      const res = await fetch(`/api/calendar/${postId}/metrics`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ impressions, reactions, comments }),
      });
      if (res.ok) {
        fetchAnalytics();
        fetchCalendar();
      }
    } catch (e) {
      alert(`Failed to record metrics: ${e}`);
    }
  };

  const handleRefreshFromChrome = async () => {
    setIsRefreshingCookies(true);
    try {
      const res = await fetch('/api/auth/cookies/refresh-chrome', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        alert('LinkedIn cookies refreshed successfully from Chrome!');
        fetchPlatforms();
      } else {
        alert(`Chrome sync: ${data.error || 'Failed to extract session cookies.'}`);
      }
    } catch (e) {
      alert(`Error syncing Chrome cookies: ${e}`);
    } finally {
      setIsRefreshingCookies(false);
    }
  };

  const handleUpdateCookies = async (liAt: string, jsessionId: string) => {
    try {
      const res = await fetch('/api/auth/cookies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ li_at: liAt, jsessionid: jsessionId }),
      });
      if (res.ok) {
        fetchPlatforms();
      }
    } catch (e) {
      alert(`Failed to save cookies: ${e}`);
    }
  };

  return (
    <div className="app-container">
      <HeaderHUD
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        safety={safety}
        platforms={platforms}
        onRefreshCookies={handleRefreshFromChrome}
        isRefreshing={isRefreshingCookies}
      />

      <main className="main-content">
        {activeTab === 'composer' && (
          <div className="composer-grid">
            <OmniComposer
              text={text}
              setText={setText}
              title={title}
              setTitle={setTitle}
              selectedPlatforms={selectedPlatforms}
              setSelectedPlatforms={setSelectedPlatforms}
              mediaPaths={mediaPaths}
              setMediaPaths={setMediaPaths}
              auditData={auditData}
              availableHooks={availableHooks}
              onBroadcast={handleBroadcast}
              isPublishing={isPublishing}
              publishResult={publishResult}
            />

            <PlatformPreview
              transformed={transformed}
              selectedPlatforms={selectedPlatforms}
              mediaPaths={mediaPaths}
            />
          </div>
        )}

        {activeTab === 'calendar' && (
          <CalendarView
            posts={calendarPosts}
            onSelectPost={(p) => {
              setText(p.text);
              setTitle(p.title);
              setSelectedPlatforms(p.target_platforms || ['linkedin', 'twitter']);
              setActiveTab('composer');
            }}
            onPublishPost={handlePublishCalendarPost}
            isPublishing={isPublishing}
          />
        )}

        {activeTab === 'analytics' && (
          <AnalyticsView
            analytics={analytics}
            onRecordMetrics={handleRecordMetrics}
            posts={calendarPosts}
          />
        )}

        {activeTab === 'settings' && (
          <SettingsView
            safety={safety}
            platforms={platforms}
            onUpdateCookies={handleUpdateCookies}
            onRefreshFromChrome={handleRefreshFromChrome}
            isRefreshing={isRefreshingCookies}
          />
        )}
      </main>
    </div>
  );
};

export default App;
