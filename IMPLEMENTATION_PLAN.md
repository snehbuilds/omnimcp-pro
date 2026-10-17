# Implementation Plan

## Project: OmniMCP Pro
**The Protocol-Native Social Media Operating System & Command Center**

---

## 1. Roadmap & Milestones Overview

| Milestone | Target Objective | Timeline / Scope |
| :--- | :--- | :--- |
| **M1: Foundation & Scaffolding** | Repository structure, `uv` workspace, FastAPI & FastMCP skeleton, session store | Days 1–2 |
| **M2: Hybrid LinkedIn Engine** | Sub-second Voyager REST client + Patchright media upload & scraping fallback | Days 3–4 |
| **M3: Omni Cross-Posting** | `BasePlatformAdapter`, X thread splitter, WordPress HTML, Threads, Facebook | Days 5–6 |
| **M4: Content Strategy & Slop** | `AuditEngine` (AI slop radar), 20 hook formulas (F01–F20), Reach-learning loop | Days 7–8 |
| **M5: Web Command Center** | Vite + React frontend: Omni Composer, Platform Preview Cards, Visual Calendar | Days 9–11 |
| **M6: Verification & Release** | Pytest suite, E2E browser verification, Dockerfile, unified `./run.sh` launcher | Days 12–13 |

---

## 2. Phase 1: Foundation & Scaffolding

### Objective
Establish the directory hierarchy, dependency management, configuration loader, and dual-transport server skeleton.

### Tasks
- [ ] **T1.1 Project Structure Scaffolding**:
  - Create `backend/` and `frontend/` folders.
  - Initialize Python 3.12 virtual environment using `uv`.
  - Configure `backend/pyproject.toml` with dependencies: `fastmcp`, `fastapi`, `uvicorn`, `patchright`, `requests`, `pydantic`, `anyio`, `pytest`.
- [ ] **T1.2 Configuration & Credential Store (`backend/src/auth/`)**:
  - Implement `SessionStore`: reads `li_at` and `JSESSIONID` from `~/.omnimcp/cookies.json` or `.env`.
  - Implement automated cookie refresher via installed Google Chrome (`cookie_refresher.py`).
- [ ] **T1.3 Protocol & API Gateway**:
  - Set up FastMCP protocol runner supporting stdio and streamable HTTP.
  - Set up FastAPI app with CORS middleware and health routes (`/api/health`).
  - Create unified root launcher script (`run.sh`).

---

## 3. Phase 2: Hybrid LinkedIn Engine

### Objective
Deliver the dual-tier publishing architecture: sub-second Voyager REST API for text posts and hardened Patchright automation for media uploads and deep scraping.

### Tasks
- [ ] **T2.1 Fast Voyager REST Client (`backend/src/platforms/linkedin/rest_client.py`)**:
  - Implement `get_current_user()` via `/voyager/api/me` (returning identity in <300ms).
  - Implement `create_text_post(text, visibility)` via `/normandyShares` with `/ugcPosts` fallback (<500ms).
  - Implement `create_comment(post_urn, text)` for fast first-comment link drops.
- [ ] **T2.2 Hardened Patchright Browser Engine (`backend/src/platforms/linkedin/browser_engine.py`)**:
  - Port Patchright stealth configuration (fingerprint coherence, client hints, WebRTC containment).
  - Implement media upload flow: file-picker handling on `input[type="file"]`, modal navigation, and post verification.
  - Port deep profile section reader (`get_person_profile`) and search tools.
- [ ] **T2.3 LinkedIn Hybrid Adapter (`backend/src/platforms/linkedin/adapter.py`)**:
  - Wire automatic routing: route text-only posts to REST Tier; route media posts and scraping to Browser Tier.
  - Integrate `SafetyGuard` (cooldown checks and daily limits).

---

## 4. Phase 3: Omni Cross-Posting & Multi-Platform Adapters

### Objective
Expand the publishing pipeline to X (Twitter), Threads, WordPress, and Facebook using a clean adapter abstraction.

### Tasks
- [ ] **T3.1 Base Architecture & Registry (`backend/src/core/`)**:
  - Implement `BasePlatformAdapter` abstract interface with `publish()`, `verify_auth()`, and `get_limits()`.
  - Implement `PlatformAdapterRegistry` with dynamic discovery and credential verification.
- [ ] **T3.2 Content Transformer (`backend/src/core/transformer.py`)**:
  - Implement sentence-aware X thread chunker (`1/n`, `2/n` formatting for >280 chars).
  - Implement WordPress Markdown-to-semantic-HTML converter.
  - Implement LinkedIn link-stripping and first-comment preparation.
- [ ] **T3.3 Concrete Platform Adapters (`backend/src/platforms/`)**:
  - X (Twitter) Adapter: Twitter API v2 thread publisher.
  - WordPress Adapter: WP REST API (`/wp/v2/posts`) with Application Passwords.
  - Threads Adapter: Meta Threads Graph API.
  - Facebook Adapter: Meta Graph API page publisher.
- [ ] **T3.4 MCP Multi-Platform Tools**:
  - Implement `omni_broadcast_post` and `omni_preview_broadcast` with dry-run capabilities.

---

## 5. Phase 4: Content Strategy, Slop Auditor & Reach Learning

### Objective
Integrate the intelligence layer: AI slop radar, 20 viral hook formulas, 7-day content calendar, and automated reach learning.

### Tasks
- [ ] **T4.1 AI-Slop & Quality Audit Engine (`backend/src/core/audit.py`)**:
  - Implement dictionary and regex scanner for 2026 AI tropes (*"delve"*, *"tapestry"*, *"in today's fast-paced"*, staccato stacks).
  - Compute a 0–100 slop penalty score.
  - Classify openings against 20 hook formulas (F01 Obituary, F02 Year-over-Year, F03 Contrarian, etc.).
- [ ] **T4.2 Content Calendar & Scheduler (`backend/src/core/scheduler.py`)**:
  - Port 7-day, 35-post content calendar covering core 2026 technical themes.
  - Implement status tracking (`PENDING`, `PUBLISHED`, `FAILED`, `SKIPPED`).
- [ ] **T4.3 Reach-Learning Feedback Loop**:
  - Implement `record_reach_metrics(post_id, impressions, reactions, comments)`.
  - Compute Engagement Velocity Ratio: `(Reactions*2 + Comments*5)/Impressions`.
  - Generate automated recommendations for future post hooks.

---

## 6. Phase 5: Web Command Center (Frontend)

### Objective
Construct a responsive, glassmorphic dark-mode web application for creator control and visual feedback.

### Tasks
- [ ] **T5.1 Frontend Scaffolding (`frontend/`)**:
  - Initialize Vite + React 19 + TypeScript.
  - Establish tokenized Vanilla CSS design system (dark mode, glassmorphic cards, typography tokens).
- [ ] **T5.2 Omni Composer & Slop Radar**:
  - Build master textarea with real-time word/character counters.
  - Build live AI-slop visual radar (highlighting flagged terms with advice).
  - Build Hook Formula selector dropdown with templates.
  - Add drag-and-drop media upload zone.
- [ ] **T5.3 Multi-Platform Live Preview Cards**:
  - LinkedIn Card component: avatar, name, headline, fold cutoff button ("...see more"), first-comment link card.
  - X (Twitter) Thread Card component: stacked tweet preview with 280-char indicators.
  - WordPress Card component: rendered HTML with code block styling.
- [ ] **T5.4 Interactive 7-Day Calendar**:
  - Responsive visual grid displaying 5 global slots per day.
  - Day theme tags (Agentic Coding, MCP, AI Code Debt, Vibe Coding, SRE, Local AI, Distribution).
  - One-click "Publish Now" button with animated progress.
- [ ] **T5.5 Analytics & Safety Dashboard**:
  - Velocity score charts and top-performing hook leaderboards.
  - Cooldown timer countdown clock and daily post limit gauge.
  - One-click Chrome cookie refresh trigger.

---

## 7. Phase 6: Testing, Hardening & Release

### Objective
Ensure rock-solid reliability across all interfaces before release.

### Tasks
- [ ] **T6.1 Unit & Integration Testing**:
  - Pytest suite covering: Transformer, AuditEngine, PlatformRegistry, SafetyGuard, Scheduler.
  - Mocked network tests for Voyager REST client and platform adapters.
- [ ] **T6.2 Live E2E Verification**:
  - Test dry-run execution across all platforms.
  - Verify live sub-second LinkedIn post publication.
  - Verify media upload via background browser.
- [ ] **T6.3 Documentation & Release Packaging**:
  - Verify `README.md`, `ARCHITECTURE.md`, `PRD.md`, `DESIGN.md`, `AGENTS.md`.
  - Create Dockerfile and docker-compose.yml.
  - Provide MCP client configurations for Claude Desktop, Cursor, and Antigravity IDE.
