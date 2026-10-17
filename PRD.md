# Product Requirements Document (PRD)

## Project: OmniMCP Pro
**The Protocol-Native Social Media Operating System & Command Center**

---

## 1. Executive Summary
**OmniMCP Pro** is an all-in-one social automation engine and developer command center built on the Model Context Protocol (MCP). It bridges autonomous LLM agents (Claude Code, Antigravity IDE, Cursor, Codex) and human creators directly with major publishing platforms: **LinkedIn, X (Twitter), Threads, WordPress, and Facebook**.

OmniMCP Pro synthesizes two complementary paradigms:
1. **High-Speed Headless Execution:** Instant, zero-overhead REST API mutations (sub-500ms LinkedIn Voyager/Flagship posts and profile checks).
2. **Stealth Browser Automation:** Hardened Patchright/Playwright browser automation for media/image attachments, deep profile scraping, search, and relationship management.

Paired with a modern, glassmorphic **Web Dashboard (Frontend)**, OmniMCP Pro provides a real-time AI-slop auditor, live multi-platform post preview cards, a 7-day visual calendar, and a closed-loop reach-learning analytics engine.

---

## 2. Problem Statement
1. **High SaaS Tolls & Fragmented Tooling:** Existing tools charge $30–$100/mo for basic scheduling APIs (Publora, Apify, Buffer), adding latency, recurring costs, and third-party data leakage.
2. **Slow Browser Execution:** Pure browser-based MCP servers take 15–30 seconds per action, creating severe bottlenecks during autonomous agent execution.
3. **Format & Algorithmic Mismatch:** Different networks penalize cross-posted content (e.g., LinkedIn suppresses reach when links are in the body; X caps at 280 characters; WordPress expects semantic HTML).
4. **AI-Slop Proliferation:** Auto-posted AI drafts suffer from cliché vocabulary (*"delve"*, *"tapestry"*, *"in today's fast-paced world"*), resulting in algorithmic demotion and reader fatigue.
5. **No Visual Feedback for Agents:** Agents lack visual interfaces to preview drafts or audit how content will appear across platforms before broadcasting.

---

## 3. Product Vision & Core Objectives
- **Zero-Cost Direct Engine:** No third-party SaaS subscriptions. Direct communication using active browser sessions, official APIs, and hardened stealth automation.
- **Dual-Tier Hybrid Publishing:**
  - **Tier 1 (Fast REST):** Sub-second text posts, comments, and profile health checks via LinkedIn's Flagship REST endpoints.
  - **Tier 2 (Stealth Browser):** Automated media file-picker for image posts, deep profile scraping, search, and direct messaging.
- **Omni Multi-Platform Cross-Posting:** One master post transformed into:
  - **LinkedIn:** 3,000-char cap, hook before the fold, external link moved to first comment.
  - **X (Twitter):** 280-char chunking into numbered `1/n` threads.
  - **Threads:** 500-char native adaptation.
  - **WordPress:** Markdown converted to semantic HTML with headings, tags, and categories.
  - **Facebook:** Clean page post formatting.
- **Real-Time Quality Guard:** Live AI-slop scoring and 20 proven viral hook formulas (F01–F20).
- **Closed-Loop Reach Learning:** Ingestion of post impressions and engagement to score velocity and recommend winning hooks for upcoming posts.
- **Full-Stack Experience:** Dual protocol server (stdio MCP for agents, FastAPI + Vite React Dashboard for humans).

---

## 4. User Personas
- **The Autonomous AI Agent:** Needs fast JSON-RPC tools over `stdio` or `HTTP` to audit, preview, and broadcast technical updates with zero human intervention.
- **The Indie Hacker & Technical Founder:** Builds in public, wants to turn code commits and release notes into cross-platform social reach from one screen.
- **The Developer Advocate & SRE:** Needs reliable, scheduled publishing of technical architecture guides, code snippets, and infographics.

---

## 5. Functional Requirements

### 5.1 Protocol & Core Engine
| ID | Requirement | Description | Priority |
| :--- | :--- | :--- | :--- |
| **FR-PR-01** | **MCP Stdio Server** | Standard JSON-RPC 2.0 over `stdio` conforming to MCP specification. | P0 |
| **FR-PR-02** | **MCP HTTP/SSE Server**| FastMCP Streamable HTTP / SSE endpoint for remote/web agents. | P0 |
| **FR-PR-03** | **FastAPI Web API** | REST API powering the Web Dashboard (calendar, compose, audit, analytics). | P0 |
| **FR-PR-04** | **SafetyGuard** | 3-minute cooldown between posts, 6 posts/day cap, randomized human jitter delays. | P0 |
| **FR-PR-05** | **Write Gate** | Strict confirmation flags (`confirm_post=True`) and environment switch (`OMNI_WRITE_ENABLED=true`). | P0 |

### 5.2 LinkedIn Hybrid Adapter
| ID | Requirement | Description | Priority |
| :--- | :--- | :--- | :--- |
| **FR-LI-01** | **Fast Voyager REST Post** | Publishes text posts via `/normandyShares` and `/rest/posts` in <500ms. | P0 |
| **FR-LI-02** | **Fast Auth & Identity** | Instant session check via `/voyager/api/me` returning vanity name, headline, and avatar. | P0 |
| **FR-LI-03** | **Browser Media Upload** | Patchright browser automation handling image file-picker, modal transitions, and upload verification. | P0 |
| **FR-LI-04** | **Comments & Replies** | Fast first-comment link drops and threaded comment replies. | P1 |
| **FR-LI-05** | **Deep Profile Scraper** | Scrapes complete profile sections (experience, education, skills, about). | P1 |
| **FR-LI-06** | **Search & Prospecting** | Global post, people, and job search with structured JSON returns. | P2 |

### 5.3 Multi-Platform Adapters (`BasePlatformAdapter`)
| ID | Requirement | Description | Priority |
| :--- | :--- | :--- | :--- |
| **FR-AD-01** | **X (Twitter) Adapter** | Publishes single tweets and automatically splits long-form text into `1/n` threads. | P0 |
| **FR-AD-02** | **WordPress Adapter** | Converts Markdown to semantic HTML and publishes via WP REST API with App Passwords. | P1 |
| **FR-AD-03** | **Meta Threads Adapter** | Publishes updates formatted to 500 characters via Threads Graph API. | P1 |
| **FR-AD-04** | **Facebook Adapter** | Publishes to connected Facebook Pages via Graph API. | P2 |
| **FR-AD-05** | **Content Transformer** | Central pipeline transforming 1 master post into per-platform optimized payloads. | P0 |

### 5.4 AI-Slop Auditor & Strategy Engine
| ID | Requirement | Description | Priority |
| :--- | :--- | :--- | :--- |
| **FR-ST-01** | **AI Slop Detection** | Flags 2026 AI tropes (*"delve"*, *"tapestry"*, *"testament"*, *"in today's fast-paced"*) and computes slop penalty score. | P0 |
| **FR-ST-02** | **Hook Classifier** | Identifies and scores drafts against 20 viral hook formulas (F01–F20). | P0 |
| **FR-ST-03** | **7-Day Calendar** | Pre-loaded 35-post tech schedule mapped across 5 global time windows. | P0 |
| **FR-ST-04** | **Reach Learning Loop** | Records reach metrics, calculates Engagement Velocity `(2*Reactions + 5*Comments)/Impressions`, and updates hook weights. | P1 |

### 5.5 Web Command Center (Frontend)
| ID | Requirement | Description | Priority |
| :--- | :--- | :--- | :--- |
| **FR-FE-01** | **Omni Composer** | Multi-platform editor with live character counters, media upload, and platform toggles. | P0 |
| **FR-FE-02** | **Live Slop Meter** | Real-time visual radar highlighting slop phrases and displaying score badge. | P0 |
| **FR-FE-03** | **Platform Preview Cards** | Interactive tabs rendering live LinkedIn card (with fold cutoff), X thread, and WP HTML. | P0 |
| **FR-FE-04** | **Interactive Calendar** | Visual schedule grid with one-click "Publish Now", "Dry Run", and status badges. | P0 |
| **FR-FE-05** | **Analytics Dashboard** | Charts for engagement velocity, hook performance rankings, and AI recommendations. | P1 |
| **FR-FE-06** | **Session & Safety Center**| Live countdown timer for cooldown, daily limit gauges, and one-click Chrome session refresh. | P1 |

---

## 6. Non-Functional Requirements
- **Performance:** REST tool response < 500ms; browser media post < 15s; local audit < 50ms.
- **Reliability:** > 99% posting success rate for active sessions with graceful fallback.
- **Security:** Zero plaintext credential logging; tokens stored strictly in local `.env` or `~/.omnimcp/` directory.
- **Portability:** Python 3.12+ (managed with `uv`), Node 20+ (Vite), cross-platform (macOS, Linux, Windows/Docker).
