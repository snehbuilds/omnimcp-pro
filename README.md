# OmniMCP Pro 🚀
### The Protocol-Native Social Media Operating System & Command Center

OmniMCP Pro is a high-performance Model Context Protocol (MCP) server and full-stack web command center designed for autonomous AI agents (Claude Code, Antigravity IDE, Cursor, Codex) and technical founders.

It combines an **instant, sub-second Voyager REST API** with a **hardened stealth browser engine (Patchright)** to automate publishing, image uploads, profile intelligence, and cross-posting across **LinkedIn, X (Twitter), Threads, WordPress, and Facebook**—completely eliminating third-party SaaS tolls (Publora, Apify).

---

## 🌟 Key Capabilities

1. **Dual-Tier Hybrid Publishing (LinkedIn):**
   - **Tier 1 (Instant REST):** Sub-second text posts (`/voyager/api/contentcreation/normandyShares` and `/rest/posts`) and auth checks (`/voyager/api/me`) completing in **~300ms to 500ms** (50x faster than browser launch).
   - **Tier 2 (Stealth Browser):** Automated media file-picker for single & multi-image uploads, deep profile scraping, search, and direct messaging via hardened Patchright.
2. **Omni Cross-Posting Engine (`ContentTransformer`):**
   - One master draft automatically adapted for each network:
     - **LinkedIn:** 3,000 char cap, hook before fold, external links moved to first comment (`🔗 Link: <url>`) to preserve algorithmic reach.
     - **X (Twitter):** 280 char cap, auto-split into numbered tweet threads (`1/n`, `2/n`).
     - **Threads:** 500 char cap.
     - **WordPress:** Markdown converted to semantic HTML (`<h1>`, `<pre><code>`, `<blockquote>`) with tags and categories.
     - **Facebook:** Clean page post formatting.
3. **Real-Time AI-Slop Radar & Hook Engine:**
   - Detects 2026 AI clichés (*"delve"*, *"tapestry"*, *"testament"*, *"in today's fast-paced digital world"*) and calculates an instant slop penalty score.
   - Built-in selector and evaluator for the **20 viral hook formulas (F01–F20)** from Serge Bulaev's framework.
4. **Interactive 7-Day Content Calendar & Reach Learning Loop:**
   - Pre-loaded with 35 technical posts mapped across 5 global time slots.
   - Measures live post engagement velocity:
     $$\text{Velocity} = \frac{(\text{Reactions} \times 2) + (\text{Comments} \times 5)}{\max(1, \text{Impressions})}$$
   - Dynamically biases future draft recommendations toward high-converting hooks.
5. **Modern Web Command Center (Frontend):**
   - Glassmorphic dark-mode web application (Vite + React 19 + TypeScript).
   - Live side-by-side platform preview cards (see exactly how your post looks on LinkedIn, X, and WordPress before publishing).
   - Visual calendar with one-click "Publish Now" triggers and live progress spinners.
6. **Enterprise Safety & Anti-Ban Architecture (`SafetyGuard`):**
   - Minimum 3-minute cooldown between automated posts.
   - Maximum 6 posts/day frequency ceiling.
   - Randomized human jitter delays (1.5s–3.5s).
   - Strict write-gate confirmation (`confirm_post=True`, `OMNI_WRITE_ENABLED=true`).

---

## 📚 Complete Project Documentation

- **[PRD.md](PRD.md)**: Product Requirements Document, user personas, and feature specifications.
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: System architecture, hybrid execution tiers, data flow diagrams, and security models.
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)**: Phase-by-phase implementation plan, task breakdown, and test strategy.
- **[DESIGN.md](DESIGN.md)**: Complete design system, color tokens, typography, component layout, and micro-interactions.
- **[AGENTS.md](AGENTS.md)**: Operational rules, invariant constraints, and guidelines for AI agents working in this repository.

---

## 🚀 Quickstart & Setup

### Prerequisites
- Python 3.12+ with [`uv`](https://github.com/astral-sh/uv)
- Node.js 20+ with `npm`
- Google Chrome installed (for automatic session cookie refresh)

### 1. Clone & Set Up Environment
```bash
cd /Users/snehashis/Projects/omnimcp-pro

# Copy sample configuration
cp .env.example .env
```

### 2. Configure Your LinkedIn Session
OmniMCP Pro reads your active session from your environment or `~/.omnimcp/cookies.json`:
```env
# In .env
LINKEDIN_LI_AT="AQEDAW-lZLs..."
LINKEDIN_CSRF_TOKEN="ajax:6834604934658236552"
LINKEDIN_JSESSIONID='"ajax:6834604934658236552"'
LINKEDIN_VANITY_NAME="snehbuilds"
OMNI_WRITE_ENABLED="true"
```
*(You can also use the one-click session refresher in the Web UI to grab cookies directly from Google Chrome!)*

### 3. Launch the Complete System
```bash
# Starts both the FastAPI Web Backend (Port 8000) and Vite Frontend (Port 5173)
./run.sh
```
Open your browser at `http://localhost:5173` to access the **OmniMCP Pro Command Center**.

---

## 🔌 Connecting to MCP Clients (Claude, Cursor, Antigravity)

Add OmniMCP Pro to your client configuration:

### Stdio Transport (`claude_desktop_config.json` or `mcp_config.json`):
```json
{
  "mcpServers": {
    "omnimcp-pro": {
      "command": "/Users/snehashis/Projects/omnimcp-pro/backend/.venv/bin/python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "/Users/snehashis/Projects/omnimcp-pro/backend",
      "env": {
        "PYTHONPATH": "/Users/snehashis/Projects/omnimcp-pro/backend"
      }
    }
  }
}
```

### Streamable HTTP Transport:
```json
{
  "mcpServers": {
    "omnimcp-pro-http": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

---

## 🧰 Available MCP Tools

| Tool | Type | Description |
|---|---|---|
| `omni_broadcast_post` | Mutating | Cross-posts content across LinkedIn, X, Threads, WordPress, and Facebook with automatic platform formatting. |
| `omni_preview_broadcast` | Read-only | Simulates the post and returns rendered previews for all target channels without executing network calls. |
| `omni_audit_content` | Read-only | Audits drafts for AI-slop vocabulary, evaluates fold length, and matches against the 20 viral hook formulas. |
| `omni_get_calendar` | Read-only | Retrieves the 7-day scheduled posts with day theme tags and status filters. |
| `omni_publish_scheduled_post` | Mutating | Publishes a scheduled post from the calendar by ID. |
| `omni_record_reach_metrics` | Mutating | Ingests live post views, reactions, and comments into the reach-learning feedback loop. |
| `omni_get_reach_recommendations` | Read-only | Analyzes historical post performance to recommend winning hooks and topics for tomorrow. |
| `linkedin_get_profile` | Read-only | Sub-second (<300ms) check of active LinkedIn session and profile identity. |
| `linkedin_create_post` | Mutating | Fast Voyager REST or Patchright image post to LinkedIn. |
| `linkedin_post_comment` | Mutating | Adds a comment or first-comment link drop to any post. |

---

## 🛡️ Anti-Ban Safety Rules

1. **3-Minute Cooldown:** Hard minimum 180s delay between consecutive posts.
2. **Daily Limit:** Capped at 6 posts per day to protect account standing.
3. **Jitter:** Randomized 1.5s–3.5s delay to emulate human rhythm.
4. **Local Isolation:** Credentials never leave your local machine.

---

## 📜 License
MIT © 2026 Snehashis
