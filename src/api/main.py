"""FastAPI Web Application Gateway for OmniMCP Pro.

Serves the REST API and Server-Sent Events (SSE) powering the
Web Command Center (Frontend) and human creator studio.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.auth.cookie_refresher import ChromeCookieRefresher
from src.auth.session_store import SessionStore
from src.core.audit import AuditEngine
from src.core.registry import global_adapter_registry
from src.core.safety import global_safety_guard
from src.core.scheduler import global_content_scheduler
from src.core.transformer import ContentTransformer
from src.platforms import initialize_all_adapters

# Initialize adapters
session_store = SessionStore()
cookie_refresher = ChromeCookieRefresher(session_store)
initialize_all_adapters(global_adapter_registry, session_store)

app = FastAPI(
    title="OmniMCP Pro Web Gateway",
    description="Protocol-Native Social Media Operating System & Command Center",
    version="1.0.0",
)

# Enable CORS for local Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request & Response Models
class AuditRequest(BaseModel):
    text: str = Field(..., description="Post content to audit for AI slop and hook classification")


class PreviewRequest(BaseModel):
    text: str
    title: Optional[str] = None
    targets: Optional[List[str]] = Field(default_factory=lambda: ["linkedin", "twitter", "wordpress", "threads", "facebook"])
    media_paths: Optional[List[str]] = Field(default_factory=list)


class BroadcastRequest(BaseModel):
    text: str
    targets: Optional[List[str]] = Field(default_factory=lambda: ["linkedin"])
    title: Optional[str] = None
    media_paths: Optional[List[str]] = Field(default_factory=list)
    confirm_post: bool = False
    dry_run: bool = False


class UpdatePostRequest(BaseModel):
    text: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None
    first_comment: Optional[str] = None
    target_platforms: Optional[List[str]] = None


class RecordMetricsRequest(BaseModel):
    impressions: int
    reactions: int
    comments: int
    shares: int = 0


class CookieUpdateRequest(BaseModel):
    li_at: str
    jsessionid: str


# REST Endpoints
@app.get("/api/health")
async def health_check():
    """Health route verifying API gateway is operational."""
    return {
        "status": "healthy",
        "service": "OmniMCP Pro Gateway",
        "version": "1.0.0",
        "timestamp": time.time(),
    }


@app.post("/api/posts/audit")
async def audit_post(req: AuditRequest):
    """Analyze post for 2026 AI slop and classify hook against F01–F20 formulas."""
    result = AuditEngine.audit_content(req.text)
    return {
        "slop_score": result.slop_score,
        "slop_rating": result.slop_rating,
        "character_count": result.character_count,
        "word_count": result.word_count,
        "reading_time_seconds": result.reading_time_seconds,
        "flagged_terms": [t.__dict__ for t in result.flagged_terms],
        "hook_detected": result.hook.__dict__ if result.hook else None,
        "advice": result.advice,
        "available_hooks": AuditEngine.get_all_hook_formulas(),
    }


@app.post("/api/posts/preview")
async def preview_post(req: PreviewRequest):
    """Generate multi-platform live preview cards (LinkedIn fold cutoff, Twitter thread chunks, WP HTML)."""
    transformed_all = ContentTransformer.transform_all(req.text, title=req.title)
    dry_run_previews = global_adapter_registry.preview_broadcast(
        text=req.text,
        targets=req.targets,
        title=req.title,
        media_paths=req.media_paths,
    )
    return {
        "transformed": {k: v.__dict__ for k, v in transformed_all.items()},
        "previews": dry_run_previews,
    }


@app.post("/api/posts/broadcast")
async def broadcast_post(req: BroadcastRequest):
    """Execute broadcast across chosen social networks with safety and write gate checks."""
    result = await global_adapter_registry.broadcast_post(
        text=req.text,
        targets=req.targets,
        title=req.title,
        media_paths=req.media_paths,
        confirm_post=req.confirm_post,
        dry_run=req.dry_run,
    )
    return result


@app.get("/api/calendar")
async def get_calendar():
    """Retrieve full 7-day, 35-post visual calendar schedule."""
    posts = global_content_scheduler.get_all_posts()
    return {
        "total": len(posts),
        "posts": [p.__dict__ for p in posts],
    }


@app.get("/api/calendar/{post_id}")
async def get_scheduled_post(post_id: str):
    """Get single scheduled post by ID."""
    post = global_content_scheduler.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post.__dict__


@app.patch("/api/calendar/{post_id}")
async def update_scheduled_post(post_id: str, req: UpdatePostRequest):
    """Update scheduled post text, title, or status."""
    post = global_content_scheduler.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if req.text is not None:
        post.text = req.text
    if req.title is not None:
        post.title = req.title
    if req.status is not None:
        post.status = req.status.upper()
    if req.first_comment is not None:
        post.first_comment = req.first_comment
    if req.target_platforms is not None:
        post.target_platforms = req.target_platforms

    global_content_scheduler.save()
    return post.__dict__


@app.post("/api/calendar/{post_id}/publish")
async def publish_calendar_post(post_id: str, confirm_post: bool = False):
    """Trigger publishing of a specific scheduled calendar item."""
    post = global_content_scheduler.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    res = await global_adapter_registry.broadcast_post(
        text=post.text,
        targets=post.target_platforms,
        title=post.title,
        media_paths=post.media_paths,
        confirm_post=confirm_post,
    )

    if not res.get("dry_run") and res.get("successful_targets", 0) > 0:
        urls = {k: v.get("url") for k, v in res.get("results", {}).items() if v.get("url")}
        global_content_scheduler.update_post_status(post_id, "PUBLISHED", published_urls=urls)

    return res


@app.post("/api/calendar/{post_id}/metrics")
async def record_calendar_metrics(post_id: str, req: RecordMetricsRequest):
    """Record reach metrics and update velocity scoring loop."""
    metrics = global_content_scheduler.record_metrics(
        post_id=post_id,
        impressions=req.impressions,
        reactions=req.reactions,
        comments=req.comments,
        shares=req.shares,
    )
    if not metrics:
        raise HTTPException(status_code=404, detail="Post not found")
    return metrics.__dict__


@app.get("/api/analytics")
async def get_analytics():
    """Get aggregated engagement velocity metrics, hook leaderboards, and AI recommendations."""
    return global_content_scheduler.get_reach_analytics()


@app.get("/api/platforms")
async def get_platforms():
    """Check configuration and live session status across all platforms."""
    status = session_store.get_all_platforms_status()
    # Check LinkedIn identity if configured
    li_status = status.get("linkedin", {})
    if li_status.get("configured"):
        li_adapter = global_adapter_registry.get("linkedin")
        if li_adapter:
            try:
                auth_info = await li_adapter.verify_auth()
                li_status["auth_info"] = auth_info
            except Exception as e:
                li_status["auth_info"] = {"authenticated": False, "error": str(e)}

    return status


@app.get("/api/safety")
async def get_safety():
    """Get live cooldown timer countdown, daily limits, and write gate switch."""
    status = global_safety_guard.get_status("linkedin")
    return status.__dict__


@app.post("/api/auth/cookies")
async def update_cookies(req: CookieUpdateRequest):
    """Manually update LinkedIn session cookies from the web dashboard."""
    result = cookie_refresher.manual_update(req.li_at, req.jsessionid)
    return result


@app.post("/api/auth/cookies/refresh-chrome")
async def refresh_cookies_from_chrome():
    """Trigger automated Patchright Chrome session extraction."""
    result = await cookie_refresher.refresh_linkedin_via_browser(headless=True)
    return result


@app.get("/api/events")
async def sse_event_stream(request: Request):
    """Server-Sent Events (SSE) stream broadcasting real-time cooldown and status updates."""

    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            status = global_safety_guard.get_status("linkedin")
            payload = {
                "cooldown_remaining": status.cooldown_remaining_seconds,
                "is_on_cooldown": status.is_on_cooldown,
                "posts_today": status.posts_today,
                "daily_limit": status.daily_limit,
                "timestamp": time.time(),
            }
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")



from fastapi.responses import HTMLResponse, RedirectResponse
from src.auth.oauth_helper import LinkedInOAuthHelper

oauth_helper = LinkedInOAuthHelper(session_store)


@app.get("/api/auth/linkedin/oauth/url")
def get_linkedin_oauth_url(client_id: Optional[str] = None, redirect_uri: Optional[str] = None):
    try:
        url = oauth_helper.get_authorization_url(client_id=client_id, redirect_uri=redirect_uri)
        return {"success": True, "auth_url": url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/auth/linkedin/callback", response_class=HTMLResponse)
async def linkedin_oauth_callback(
    code: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
):
    if error:
        return HTMLResponse(
            content=f"""
            <html><body style="font-family: sans-serif; background: #090a0f; color: #f43f5e; padding: 40px; text-align: center;">
                <h2>❌ LinkedIn OAuth Authorization Failed</h2>
                <p>{error}: {error_description}</p>
                <br/>
                <a href="/" style="color: #38bdf8;">Return to Command Center</a>
            </body></html>
            """,
            status_code=400,
        )

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code parameter")

    result = await oauth_helper.exchange_code_for_token(code=code)
    if result.get("success"):
        return HTMLResponse(
            content="""
            <html><body style="font-family: sans-serif; background: #090a0f; color: #f8fafc; padding: 40px; text-align: center;">
                <div style="max-width: 500px; margin: 40px auto; background: #121520; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 30px;">
                    <h2 style="color: #10b981; margin-top: 0;">✅ LinkedIn Official OAuth Connected!</h2>
                    <p style="color: #94a3b8;">Your official OAuth 2.0 access token has been acquired and saved to .env.</p>
                    <p style="color: #64748b; font-size: 13px;">Scopes: openid, profile, email, w_member_social</p>
                    <br/>
                    <a href="/" style="display: inline-block; background: #38bdf8; color: #090a0f; padding: 10px 24px; border-radius: 6px; font-weight: 600; text-decoration: none;">Return to Command Center</a>
                </div>
            </body></html>
            """
        )

    return HTMLResponse(
        content=f"""
        <html><body style="font-family: sans-serif; background: #090a0f; color: #f43f5e; padding: 40px; text-align: center;">
            <h2>❌ Token Exchange Failed</h2>
            <p>{result.get('error')}</p>
            <br/>
            <a href="/" style="color: #38bdf8;">Return to Command Center</a>
        </body></html>
        """,
        status_code=400,
    )


# Mount static frontend build if present
dist_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")
