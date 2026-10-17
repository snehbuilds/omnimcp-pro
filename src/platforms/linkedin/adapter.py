"""LinkedIn Hybrid Adapter for OmniMCP Pro.

Implements BasePlatformAdapter with intelligent dual-tier routing:
- Tier 1 (Voyager REST): Fast sub-second text posts, profile health checks, comments.
- Tier 2 (Patchright Browser): Media/image uploads and fallback.
"""

from __future__ import annotations

import sys
import time
from typing import Any, Dict, Optional

from src.auth.session_store import SessionStore
from src.core.adapter_base import BasePlatformAdapter, PlatformLimits, PublishPayload, PublishResult

from .browser_engine import LinkedInBrowserEngine
from .rest_client import LinkedInRestClient


class LinkedInAdapter(BasePlatformAdapter):
    """The hybrid LinkedIn publishing and scraping adapter."""

    def __init__(
        self,
        session_store: Optional[SessionStore] = None,
        rest_client: Optional[LinkedInRestClient] = None,
        browser_engine: Optional[LinkedInBrowserEngine] = None,
    ):
        super().__init__(name="linkedin")
        self.session_store = session_store or SessionStore()
        self.rest_client = rest_client or LinkedInRestClient(self.session_store)
        self.browser_engine = browser_engine or LinkedInBrowserEngine(self.session_store)

    def get_limits(self) -> PlatformLimits:
        return PlatformLimits(
            name="linkedin",
            max_characters=3000,
            allows_media=True,
            max_media_count=9,
            supported_media_types=["image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4"],
            supports_markdown=False,
            supports_threads=False,
            rate_limit_per_day=6,  # Strict anti-ban ceiling
        )

    async def verify_auth(self) -> Dict[str, Any]:
        """Check session health via fast /voyager/api/me REST call (<300ms)."""
        return await self.rest_client.get_current_user()

    async def publish(self, payload: PublishPayload) -> PublishResult:
        """Route to appropriate execution tier based on media presence and dry-run state."""
        start_time = time.time()

        # Handle Dry-Run Mode
        if payload.dry_run:
            elapsed = round((time.time() - start_time) * 1000, 2)
            tier = "patchright_browser (dry-run)" if payload.media_paths else "voyager_rest (dry-run)"
            return PublishResult(
                success=True,
                platform="linkedin",
                post_id="dryrun-li-activity-preview",
                url="https://www.linkedin.com/feed/update/urn:li:activity:preview",
                execution_time_ms=elapsed,
                tier_used=tier,
                first_comment_id="dryrun-comment-preview" if payload.first_comment else None,
                warnings=["Simulated dry-run: No external network mutation made."],
            )

        # Tier 2: Media uploads strictly use Patchright browser
        if payload.media_paths:
            sys.stderr.write("[LinkedInAdapter] Media detected: Routing to Tier 2 (Patchright Browser)...\n")
            success, act_urn, post_url, elapsed, err = await self.browser_engine.publish_media_post(
                text=payload.text,
                media_paths=payload.media_paths,
                visibility=payload.visibility,
            )
            return PublishResult(
                success=success,
                platform="linkedin",
                post_id=act_urn,
                url=post_url,
                execution_time_ms=elapsed,
                tier_used="patchright_browser",
                error=err,
            )

        # Tier 1: Sub-second Voyager REST API for text-only posts
        sys.stderr.write("[LinkedInAdapter] Text-only: Routing to Tier 1 (Voyager REST Client)...\n")
        success, act_urn, post_url, elapsed, err = await self.rest_client.create_text_post(
            text=payload.text,
            visibility=payload.visibility,
        )

        comment_id = None
        warnings = []

        # If post succeeded and there is a first comment (e.g., extracted external URL)
        if success and act_urn and payload.first_comment:
            c_ok, c_urn, c_err = await self.rest_client.create_comment(
                activity_urn=act_urn,
                comment_text=payload.first_comment,
            )
            if c_ok:
                comment_id = c_urn
            else:
                warnings.append(f"Post succeeded, but first-comment drop failed: {c_err}")

        # Fallback to browser if REST encounters an auth challenge or error
        if not success and ("unauthorized" in str(err).lower() or "checkpoint" in str(err).lower()):
            sys.stderr.write(f"[LinkedInAdapter] Voyager REST failed ({err}). Attempting Tier 2 browser fallback...\n")
            fb_success, fb_urn, fb_url, fb_elapsed, fb_err = await self.browser_engine.publish_media_post(
                text=payload.text,
                media_paths=[],
                visibility=payload.visibility,
            )
            return PublishResult(
                success=fb_success,
                platform="linkedin",
                post_id=fb_urn,
                url=fb_url,
                execution_time_ms=elapsed + fb_elapsed,
                tier_used="patchright_browser_fallback",
                error=fb_err if not fb_success else None,
                warnings=["Used browser fallback after REST authentication challenge."],
            )

        return PublishResult(
            success=success,
            platform="linkedin",
            post_id=act_urn,
            url=post_url,
            execution_time_ms=elapsed,
            tier_used="voyager_rest",
            first_comment_id=comment_id,
            error=err,
            warnings=warnings,
        )
