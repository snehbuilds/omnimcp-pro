"""FastMCP Protocol Server for OmniMCP Pro.

Unified server combining:
1. Complete LinkedIn MCP Suite (30 tools: profiles, company, jobs, feed, messaging, posts, comments, reactions).
2. Omni Multi-Platform Engine (Cross-posting to X/Twitter, Threads, WordPress, Facebook).
3. Strategy & Reach Learning (AI-Slop Radar, 20 Hook Formulas, 7-Day Calendar, Engagement Velocity Loop).
4. Fast Sub-Second Voyager REST Tier (<500ms text posting & session checks).

CRITICAL INVARIANT:
- Never write logs or raw prints to stdout.
- Stdout is strictly reserved for JSON-RPC 2.0 messages.
- All logs and diagnostic output must write strictly to sys.stderr.
"""

from __future__ import annotations

import logging
import sys
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from src.core.audit import AuditEngine
from src.core.registry import global_adapter_registry
from src.core.safety import global_safety_guard
from src.core.scheduler import global_content_scheduler
from src.platforms import initialize_all_adapters

# Configure logging strictly to sys.stderr
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("OmniMCP")

# Initialize registry and adapters
initialize_all_adapters(global_adapter_registry)

# Create FastMCP instance
mcp = FastMCP(
    name="OmniMCP Pro",
)

# ==============================================================================
# 1. Mount Complete LinkedIn MCP Server Tool Suites (Browser & Extractor)
# ==============================================================================
try:
    from linkedin_mcp_server.tools.person import register_person_tools
    from linkedin_mcp_server.tools.company import register_company_tools
    from linkedin_mcp_server.tools.job import register_job_tools
    from linkedin_mcp_server.tools.messaging import register_messaging_tools
    from linkedin_mcp_server.tools.feed import register_feed_tools
    from linkedin_mcp_server.tools.post import register_post_tools
    from linkedin_mcp_server.tools.post_publishing import register_post_publishing_tools
    from linkedin_mcp_server.tools.profile_edit import register_profile_edit_tools
    from linkedin_mcp_server.tools.connection_removal import register_connection_removal_tools

    register_person_tools(mcp)
    register_company_tools(mcp)
    register_job_tools(mcp)
    register_messaging_tools(mcp)
    register_feed_tools(mcp)
    register_post_tools(mcp)
    register_post_publishing_tools(mcp)
    register_profile_edit_tools(mcp)
    register_connection_removal_tools(mcp)
    logger.info("Successfully mounted all LinkedIn MCP Server tool suites (30 tools)")
except Exception as exc:
    logger.warning("Failed to mount full linkedin_mcp_server tools: %s", exc)


# ==============================================================================
# 2. Omni Multi-Platform Tools (LinkedIn, Twitter/X, WordPress, Threads, Facebook)
# ==============================================================================

@mcp.tool()
async def omni_broadcast_post(
    text: str,
    targets: Optional[List[str]] = None,
    title: Optional[str] = None,
    media_paths: Optional[List[str]] = None,
    confirm_post: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Broadcast a post across selected platforms (LinkedIn, Twitter/X, WordPress, Threads, Facebook).

    Enforces:
    - 180s cooldown and 6 posts/day safety ceilings.
    - Write Gate: Requires confirm_post=True AND OMNI_WRITE_ENABLED=true in .env to execute live mutations.
    - Platform-specific transformations (LinkedIn 1st-comment link drops, Twitter thread chunking).

    Args:
        text: Master post text to publish.
        targets: Target platform names (e.g. ['linkedin', 'twitter']). Defaults to ['linkedin'].
        title: Optional title (used for WordPress article heading).
        media_paths: Optional list of local image/media file paths to attach.
        confirm_post: Must be True to execute live mutation. If False, returns dry-run preview.
        dry_run: Force dry-run preview without making external calls.
    """
    logger.info("Invoked omni_broadcast_post for targets=%s confirm_post=%s", targets, confirm_post)
    return await global_adapter_registry.broadcast_post(
        text=text,
        targets=targets,
        title=title,
        media_paths=media_paths,
        confirm_post=confirm_post,
        dry_run=dry_run,
    )


@mcp.tool()
def omni_preview_broadcast(
    text: str,
    targets: Optional[List[str]] = None,
    title: Optional[str] = None,
    media_paths: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Preview how a post will be formatted across platforms without making any network calls.

    Generates LinkedIn fold cutoffs, first-comment link drops, and X numbered thread splits.
    """
    return global_adapter_registry.preview_broadcast(
        text=text,
        targets=targets,
        title=title,
        media_paths=media_paths,
    )


@mcp.tool()
def omni_audit_content(text: str) -> Dict[str, Any]:
    """Scan content for 2026 AI tropes, compute 0–100 Slop Penalty Score, and classify hook formula.

    Detects cliché vocabulary ('delve', 'tapestry', 'in today's fast-paced world') and
    matches opening lines against 20 viral hook formulas (F01–F20).
    """
    audit = AuditEngine.audit_content(text)
    return {
        "slop_score": audit.slop_score,
        "slop_rating": audit.slop_rating,
        "character_count": audit.character_count,
        "word_count": audit.word_count,
        "reading_time_seconds": audit.reading_time_seconds,
        "flagged_terms": [t.__dict__ for t in audit.flagged_terms],
        "hook_detected": audit.hook.__dict__ if audit.hook else None,
        "advice": audit.advice,
    }


@mcp.tool()
def omni_get_calendar() -> Dict[str, Any]:
    """Retrieve the full 7-day, 35-post pre-loaded technical content calendar and execution statuses."""
    posts = global_content_scheduler.get_all_posts()
    return {
        "total_posts": len(posts),
        "posts": [p.__dict__ for p in posts],
    }


@mcp.tool()
async def omni_publish_scheduled_post(
    post_id: str,
    confirm_post: bool = False,
) -> Dict[str, Any]:
    """Execute publishing of a scheduled post from the 7-day calendar.

    Args:
        post_id: ID of the scheduled post (e.g., 'post-d1-s1').
        confirm_post: Must be True to authorize live publishing.
    """
    post = global_content_scheduler.get_post_by_id(post_id)
    if not post:
        return {"success": False, "error": f"Post ID '{post_id}' not found in calendar"}

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


@mcp.tool()
def omni_record_reach_metrics(
    post_id: str,
    impressions: int,
    reactions: int,
    comments: int,
    shares: int = 0,
) -> Dict[str, Any]:
    """Record reach metrics for a published post and update the reach-learning velocity loop."""
    metrics = global_content_scheduler.record_metrics(
        post_id=post_id,
        impressions=impressions,
        reactions=reactions,
        comments=comments,
        shares=shares,
    )
    if not metrics:
        return {"success": False, "error": f"Post '{post_id}' not found"}

    analytics = global_content_scheduler.get_reach_analytics()
    return {
        "success": True,
        "post_id": post_id,
        "velocity_score": metrics.velocity_score,
        "updated_rankings": analytics.get("hook_rankings", []),
    }


@mcp.tool()
def omni_get_reach_recommendations() -> Dict[str, Any]:
    """Analyze historical post performance to recommend winning hooks, categories, and optimal post timings."""
    return global_content_scheduler.get_reach_analytics()


@mcp.tool()
def omni_get_safety_status(platform: str = "linkedin") -> Dict[str, Any]:
    """Get live cooldown countdown, daily limits, and Write Gate authorization status."""
    status = global_safety_guard.get_status(platform)
    return status.__dict__


# ==============================================================================
# 3. High-Speed Sub-Second Voyager REST Tools (Fast Tier)
# ==============================================================================

@mcp.tool()
async def linkedin_fast_auth_check() -> Dict[str, Any]:
    """Sub-second (<300ms) LinkedIn identity and session validity check via Voyager REST /api/me."""
    adapter = global_adapter_registry.get("linkedin")
    if not adapter:
        return {"authenticated": False, "error": "LinkedIn adapter not loaded"}
    return await adapter.verify_auth()


@mcp.tool()
async def linkedin_fast_text_post(
    text: str,
    visibility: str = "PUBLIC",
    first_comment: Optional[str] = None,
    confirm_post: bool = False,
) -> Dict[str, Any]:
    """Sub-second (~400ms) text post directly via LinkedIn's Flagship Voyager REST API.

    Bypasses browser launch overhead for instant publishing when no media is attached.
    """
    if not confirm_post:
        return {
            "success": True,
            "dry_run": True,
            "text": text,
            "visibility": visibility,
            "first_comment": first_comment,
            "notice": "Dry-run mode. Pass confirm_post=True to publish live.",
        }

    from src.platforms.linkedin.rest_client import LinkedInRestClient
    client = LinkedInRestClient()
    success, act_urn, post_url, elapsed, err = await client.create_text_post(text, visibility=visibility)
    
    comment_urn = None
    if success and act_urn and first_comment:
        c_ok, c_urn, _ = await client.create_comment(act_urn, first_comment)
        if c_ok:
            comment_urn = c_urn

    return {
        "success": success,
        "activity_urn": act_urn,
        "post_url": post_url,
        "first_comment_urn": comment_urn,
        "execution_time_ms": elapsed,
        "error": err,
    }



@mcp.tool()
async def linkedin_check_session() -> Dict[str, Any]:
    """Instant (<300ms) LinkedIn identity and session validity check via Voyager REST /api/me."""
    adapter = global_adapter_registry.get("linkedin")
    if not adapter:
        return {"authenticated": False, "error": "LinkedIn adapter not loaded"}
    return await adapter.verify_auth()


@mcp.tool()
async def linkedin_scrape_profile(vanity_name: str) -> Dict[str, Any]:
    """Scrape public/connected profile sections via Patchright stealth browser."""
    from src.platforms.linkedin.browser_engine import LinkedInBrowserEngine

    engine = LinkedInBrowserEngine()
    return await engine.scrape_person_profile(vanity_name=vanity_name)


def run_stdio_server():
    """Run FastMCP JSON-RPC server over stdio."""
    logger.info("Starting OmniMCP Pro stdio transport runner...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_stdio_server()
