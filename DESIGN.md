# Design System & UI/UX Specification

## Project: OmniMCP Pro Web Command Center

---

## 1. Aesthetic Vision & Design Philosophy

The OmniMCP Pro Web Command Center is crafted as a **premium, mission-control studio** for autonomous agents and technical founders. It adheres to three core tenets:

1. **Dark-Mode Glassmorphism:** Deep, layered background surfaces (`#090a0f`, `#121520`) with subtle backdrop blurs, delicate 1px border highlights, and vibrant neon status accents.
2. **Instant Visual Clarity:** Zero visual clutter. Clear typographical hierarchy with high contrast, enabling creators to review and broadcast content across 5 platforms at a glance.
3. **Fluid Micro-Interactions:** Tactile feedback on buttons, smooth tab transitions, animated radar indicators for AI-slop scoring, and animated progress spinners during live network broadcasts.

---

## 2. Color Palette & Token System

### 2.1 Color Tokens (CSS Custom Properties)

```css
:root {
  /* Surface & Backgrounds */
  --bg-primary: #090a0f;
  --bg-secondary: #111420;
  --bg-tertiary: #191e30;
  --bg-elevated: rgba(25, 30, 48, 0.7);
  --bg-glass: rgba(18, 22, 36, 0.65);
  
  /* Borders & Dividers */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-medium: rgba(255, 255, 255, 0.14);
  --border-glow: rgba(56, 189, 248, 0.35);

  /* Brand Accents */
  --accent-cyan: #38bdf8;
  --accent-blue: #3b82f6;
  --accent-purple: #8b5cf6;
  --accent-green: #10b981;
  --accent-amber: #f59e0b;
  --accent-rose: #f43f5e;

  /* Platform Identity Colors */
  --color-linkedin: #0a66c2;
  --color-twitter: #1d9bf0;
  --color-threads: #ffffff;
  --color-wordpress: #21759b;
  --color-facebook: #1877f2;

  /* Typography Colors */
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --text-inverse: #0f172a;

  /* Status Tokens */
  --status-pending: #f59e0b;
  --status-published: #10b981;
  --status-failed: #f43f5e;
  --status-cooldown: #8b5cf6;

  /* Effects */
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.5);
  --shadow-glow: 0 0 20px rgba(56, 189, 248, 0.25);
  --backdrop-blur: blur(12px);
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-full: 9999px;
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 250ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## 3. Typography System

- **Primary UI Font:** `'Inter'`, system-ui, -apple-system, sans-serif. Clean, modern legibility.
- **Display & Headings:** `'Outfit'`, `'Inter'`, sans-serif. High impact, technical authority.
- **Code, Metrics & Tokens:** `'JetBrains Mono'`, `'Fira Code'`, monospace. For payload previews, tokens, and countdown timers.

### Typographic Scale
- **Display 1:** `28px` / `1.2` (Page & view titles, bold 700)
- **Heading 2:** `20px` / `1.3` (Card titles, section headers, semibold 600)
- **Heading 3:** `16px` / `1.4` (Sub-headers, component titles, semibold 600)
- **Body Regular:** `14px` / `1.5` (Inputs, post content, regular 400)
- **Body Small:** `12px` / `1.4` (Badges, metadata, timestamps, medium 500)
- **Micro Mono:** `11px` / `1.2` (Counters, status hashes, URNs, monospace 400)

---

## 4. Layout Architecture & Navigation

The layout follows a responsive 3-section layout:
1. **Top HUD & Navigation Bar (Height: 64px):**
   - Brand logo & version badge (`OmniMCP Pro v1.0`).
   - Platform connection pills (LinkedIn, X, Threads, WP, FB) with live pulse indicators.
   - Safety Status HUD: Cooldown countdown clock (`Next post in: 02:45`) and Daily limit gauge (`2/6 used`).
   - One-Click Chrome Session Refresh trigger.
2. **Main Workspace:**
   - Tab Navigation:
     - ✍️ **Composer & Slop Radar** (Publish & Preview)
     - 📅 **7-Day Content Calendar** (Schedule & Timeline)
     - 📈 **Reach Learning Lab** (Analytics & Recommendations)
     - 🔍 **LinkedIn Explorer** (Profile Scraper & DMs)
     - ⚙️ **Settings & Safety** (Keys & Cooldowns)
3. **Status Bar (Bottom: 32px):**
   - Server connectivity indicator (`FastAPI :8000 OK`, `MCP stdio OK`).
   - Active profile badge (`Connected as: @snehbuilds`).
   - Write Gate status indicator (`🔒 Write Enabled`).

---

## 5. Core View Specifications

### 5.1 The Omni Composer & AI-Slop Radar

The central creative command center:
- **Left Panel (Composer):**
  - Master auto-resizing text editor with character and word counters.
  - **Live Slop Highlighter**: Real-time underline for synthetic tropes (*"delve"*, *"tapestry"*, *"in today's fast-paced"*).
  - **Hook Selector (F01–F20)**: Dropdown offering 20 proven hooks with instant insertions:
    - *F01 Obituary / R.I.P.*: "[Concept] is dead. In 2024..."
    - *F02 Year-over-Year*: "[Time 1]: [Situation]. Today: [Shift]..."
    - *F03 Contrarian*: "Most engineers believe [Common Belief]. They are wrong..."
  - **Media Dropzone**: Drag-and-drop file upload with live image thumbnail preview.
  - **First-Comment Link Field**: Auto-extracts links from body into the first-comment field to avoid algorithmic penalties.
  - **Action Bar**:
    - "Audit Content" button (triggers full score breakdown).
    - "Dry Run Preview" button (validates across all adapters without posting).
    - "Broadcast Post" primary button (glowing gradient with live progress spinner).

- **Right Panel (Live Platform Preview Cards):**
  - Tabbed interface switching between:
    1. **LinkedIn Card**: Faithfully reproduces LinkedIn's feed UI (avatar, name, headline, post text with "...see more" fold cutoff at 140 chars, attached image, and pinned first-comment card).
    2. **X (Twitter) Thread Card**: Shows stacked cards demonstrating how text >280 chars is chunked into `1/n`, `2/n` with character count boundary rings.
    3. **WordPress Card**: Live rendered semantic HTML preview with code snippet highlighting and category tags.

### 5.2 Real-Time AI Slop Radar Badge

- A radial gauge widget showing the **Slop Score (0 to 100)**:
  - `0–15`: **Human / Organic** (Green `#10b981`)
  - `16–35`: **Low Slop** (Yellow `#f59e0b`)
  - `36+`: **Synthetic AI Cliché** (Red `#f43f5e`)
- Detailed breakdown drawer listing:
  - Identified clichés and suggested organic replacements.
  - Opening hook formula classification and retention score.
  - Fold retention analysis (is the key insight visible before the user clicks "...see more"?).

### 5.3 7-Day Interactive Visual Calendar

- 7 horizontal or grid columns (Days 1–7), each featuring 5 chronological time slots:
  - `08:15 AM IST`: APAC Morning
  - `12:30 PM IST`: Europe Start / India Lunch
  - `04:15 PM IST`: US East Wake-up
  - `07:45 PM IST`: Peak Global Overlap
  - `10:30 PM IST`: US West Lunch / East Wrap-up
- Card elements:
  - Daily theme badge (e.g. *Agentic Coding*, *MCP Standards*, *AI Code Debt*).
  - Hook formula tag (e.g. `F01`, `F02`).
  - Text preview snippet.
  - Status badge: `PENDING` (Amber), `PUBLISHED` (Green), `FAILED` (Red).
  - Quick-action buttons: "Publish Now", "Preview", "Edit Copy".

### 5.4 Reach-Learning Analytics Lab

- **Engagement Velocity Gauge**:
  - Displays computed metric: `Velocity = (2*Reactions + 5*Comments) / Impressions`.
- **Hook Performance Leaderboard**:
  - Bar chart ranking F01–F20 by conversion rate and comment count.
- **Next Post Recommender Card**:
  - High-converting prompt suggestions based on yesterday's metrics.

---

## 6. Micro-Interactions & Motion Design

1. **Button Hover & Click**:
   - Subtle scale-up (`scale(1.02)`) on hover; click scales to `scale(0.98)`.
   - Primary action buttons feature an animated radial gradient border on hover.
2. **Tab Transitions**:
   - Smooth horizontal slide and opacity fade (`opacity: 0 -> 1`, `transform: translateY(4px) -> translateY(0)` over `200ms`).
3. **Live Broadcasting Animation**:
   - When "Broadcast Post" is triggered, the button transitions into a step-by-step progress checklist:
     - `✓ LinkedIn Voyager REST: Published (412ms)`
     - `✓ X Thread Splitter: 2 Tweets Dispatched`
     - `✓ Complete`
4. **Toast Notifications**:
   - Floating glassmorphic toasts in the bottom-right corner for success/error events.
