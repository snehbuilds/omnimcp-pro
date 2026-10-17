# AGENTS.md

This file provides rules, architectural invariants, and operational guidelines for AI coding agents (Claude Code, Antigravity IDE, Cursor, Codex) working within the `omnimcp-pro` repository.

---

## 1. Development Commands

### Backend (Python 3.12 + `uv`)
- **Sync dependencies:** `uv sync` (or `uv pip install -e .`)
- **Lint code:** `uv run ruff check .` (auto-fix: `uv run ruff check --fix .`)
- **Format code:** `uv run ruff format .`
- **Run tests:** `uv run pytest` (with coverage: `uv run pytest --cov`)
- **Run FastAPI server:** `uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload`
- **Run MCP stdio server:** `uv run -m src.mcp_server.server`

### Frontend (Node 20+ + `npm` / `vite`)
- **Install dependencies:** `npm install`
- **Run local dev server:** `npm run dev`
- **Build production bundle:** `npm run build`
- **Lint:** `npm run lint`

### Unified Root Launcher
- **Launch both backend and frontend:** `./run.sh`

---

## 2. Architectural Invariants

### 2.1 The Hybrid LinkedIn Publishing Hierarchy
- **Tier 1 (Voyager REST API) is the default for text:**
  - Always use `LinkedInRestClient` (`/voyager/api/contentcreation/normandyShares` with `/ugcPosts` fallback) for text-only posts, comments, and profile health checks (`/voyager/api/me`).
  - Text posts MUST complete in under 1 second. Never launch a headless browser for simple text posting.
- **Tier 2 (Patchright Browser) is strictly for media, deep scraping, and fallback:**
  - Launch the browser only when `media_paths` are present (image uploads), deep section scraping is required (`get_person_profile`), or the REST client receives an authentication challenge.
  - Browser automation must always use **Patchright** with consistent client hints and stealth flags. Never use plain, unmasked Playwright.

### 2.2 Stdio Transport Hygiene
- **Never pollute `stdout` with logs or debug prints.**
- The MCP protocol relies on `stdout` and `stdin` for JSON-RPC 2.0 communication. Any raw `print()` statement or un-redirected logger output will corrupt the JSON stream and crash connected agent clients.
- Always configure logging handlers to write strictly to `sys.stderr`.

### 2.3 The Adapter Abstraction
- All social networks must inherit from `BasePlatformAdapter` in `core/adapter_base.py`.
- Platform-specific logic (e.g. character chunking for X, Markdown-to-HTML for WordPress, link extraction for LinkedIn) must be encapsulated in `ContentTransformer`. Do not hardcode platform quirks in the tool handlers.

---

## 3. Profile & Anti-Ban Safety Rules

### 3.1 Strict Anti-Ban Guard (`SafetyGuard`)
- **Cooldown Enforcement:** A strict minimum cooldown of **180 seconds (3 minutes)** is enforced between any two live publishing events. Agents must not bypass this check unless explicitly executing with `dry_run=True`.
- **Daily Frequency Ceiling:** Maximum **6 posts per day** on LinkedIn. The guard must reject calls exceeding this quota.
- **Human Jitter Delays:** Live network requests must inject a randomized sleep delay between 1.5s and 3.5s to prevent robotic request cadence.

### 3.2 The Write Gate
- Mutating operations (`omni_broadcast_post`, `linkedin_create_post`, `comment_on_post`) require explicit confirmation parameters (`confirm_post=True`).
- In addition, the environment variable `OMNI_WRITE_ENABLED=true` must be set in `.env` to execute live mutations on external platforms.
- If unconfirmed or disabled, the tool MUST return a preview dry-run response without making external network calls.

### 3.3 Credential Isolation & Privacy
- **Never commit `.env` or files containing session tokens.**
- Never echo raw session cookies (`li_at`, `JSESSIONID`) or API secret keys back into the LLM chat context in plaintext. Mask them (e.g. `AQED...4Awt`).
- Session cookies reside in `~/.omnimcp/cookies.json` or `.env`.

---

## 4. Frontend & Design Guidelines

- **Vanilla CSS Tokens:** Always use the design tokens defined in `DESIGN.md` (`--bg-primary`, `--accent-cyan`, `--border-subtle`, etc.). Do NOT invent random ad-hoc colors or inline styles.
- **Dark Mode First:** The UI is designed around an ultra-clean, high-contrast dark theme with glassmorphic cards and crisp borders.
- **Rich Interactive States:** Ensure all buttons, toggles, and cards have hover states, active transitions, and accessible unique IDs (`id="composer-textarea"`, `id="btn-broadcast"`).
- **Zero Mock Placeholders:** If an image is needed, use real generated infographics or SVGs. Never display broken placeholder boxes.

---

## 5. Testing & Verification Rules

- **Tests must never make live external mutations:**
  - Automated tests running in CI or `pytest` must mock all external HTTP and browser calls.
  - Test suites must complete in temporary directories (`tmp_path`) and never alter the user's active `~/.omnimcp/` session.
- **Tautology Prohibition:**
  - Assert real observable contracts. Mutate the code under test to introduce a regression and verify that the test fails before approving.
