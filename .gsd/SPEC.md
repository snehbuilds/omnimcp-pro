# SPEC.md — Project Specification

> **Status**: `FINALIZED`
>
> ⚠️ **Planning Lock**: Requirements finalized. Implementation authorized.

## Vision
**OmniMCP Pro** is an all-in-one, protocol-native social media operating system and developer command center built on the Model Context Protocol (MCP). It bridges autonomous LLM agents (Claude Code, Antigravity IDE, Cursor, Codex) and human creators directly with major publishing platforms: **LinkedIn, X (Twitter), Threads, WordPress, and Facebook**.

OmniMCP Pro synthesizes two complementary paradigms:
1. **High-Speed Headless Execution:** Instant, zero-overhead REST API mutations (sub-500ms LinkedIn Voyager/Flagship posts and profile checks).
2. **Stealth Browser Automation:** Hardened Patchright/Playwright browser automation for media/image attachments, deep profile scraping, search, and relationship management.

Paired with a modern, glassmorphic **Web Command Center (Frontend)**, OmniMCP Pro provides a real-time AI-slop radar, live multi-platform post preview cards, a 7-day visual calendar, and a closed-loop reach-learning analytics engine.

## Goals
1. **Zero-Cost Direct Engine** — No third-party SaaS subscriptions (Buffer, Publora, Apify). Direct communication using active browser sessions, official APIs, and hardened stealth automation.
2. **Dual-Tier Hybrid Publishing** — Sub-second text posts via LinkedIn Flagship REST endpoints; automated file-picker media uploads and deep scraping via Patchright browser.
3. **Omni Multi-Platform Cross-Posting** — One master post transformed into platform-native formats (LinkedIn 3,000 chars with 1st-comment link drops, X 280-char numbered threads, Threads 500 chars, WordPress semantic HTML, Facebook page posts).
4. **Real-Time Quality Guard** — Live AI-slop scoring (detecting 2026 AI clichés) and classification against 20 viral hook formulas (F01–F20).
5. **Closed-Loop Reach Learning** — Ingestion of impressions and engagement to score velocity and recommend winning hooks.
6. **Full-Stack Dual-Protocol Architecture** — FastMCP stdio/HTTP server for AI coding agents paired with FastAPI + Vite React web dashboard for human creators.

## Non-Goals (Out of Scope)
- Relying on paid intermediary scheduling SaaS APIs.
- Replacing full-fledged CRM databases (focus is protocol-native publishing, scraping, auditing, and analytics).
- Plain unmasked Playwright (Patchright stealth is mandatory to avoid bot detection).

## Constraints
- **Python 3.12 + `uv`** for the backend.
- **Node 20+ + Vite + React 19 + TypeScript + Vanilla CSS** for the frontend.
- **Strict Anti-Ban Guard**: Minimum 180s cooldown, max 6 posts/day on LinkedIn, human jitter delays (1.5s–3.5s).
- **Write Gate**: Mutating operations require `confirm_post=True` or `OMNI_WRITE_ENABLED=true`. Dry-run preview otherwise.
- **Stdio Hygiene**: Zero raw `print()` statements to `stdout` in MCP server mode; all logging to `sys.stderr`.

## Success Criteria
- [x] SPEC finalized and approved.
- [ ] Backend dual-transport gateway operational (FastMCP stdio/SSE + FastAPI REST).
- [ ] LinkedIn REST client publishes text posts and verifies profile in <500ms.
- [ ] Patchright browser engine handles media uploads and deep scraping.
- [ ] Cross-platform adapters (X threads, WP HTML, Threads, FB) operational.
- [ ] AI-slop radar and 20 hook formulas verified.
- [ ] Glassmorphic Web Command Center renders Omni Composer, preview cards, visual calendar, and safety HUD.
- [ ] Test suite passing with mocked network calls and real contract validation.

---

*Last updated: 2026-10-17*
