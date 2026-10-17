"""Facebook Adapter for OmniMCP Pro."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx

from src.auth.session_store import SessionStore
from src.core.adapter_base import BasePlatformAdapter, PlatformLimits, PublishPayload, PublishResult


class FacebookAdapter(BasePlatformAdapter):
    """Publishes page updates via Meta Graph API."""

    def __init__(self, session_store: Optional[SessionStore] = None):
        super().__init__(name="facebook")
        self.session_store = session_store or SessionStore()

    def get_limits(self) -> PlatformLimits:
        return PlatformLimits(
            name="facebook",
            max_characters=63206,
            allows_media=True,
            max_media_count=10,
            rate_limit_per_day=50,
        )

    async def verify_auth(self) -> Dict[str, Any]:
        creds = self.session_store.get_platform_credentials("facebook")
        return {"authenticated": creds.get("configured", False)}

    async def publish(self, payload: PublishPayload) -> PublishResult:
        start_time = time.time()

        if payload.dry_run:
            elapsed = round((time.time() - start_time) * 1000, 2)
            return PublishResult(
                success=True,
                platform="facebook",
                post_id="dryrun-fb-post-1",
                url="https://facebook.com/page/posts/123",
                execution_time_ms=elapsed,
                tier_used="facebook_graph_api (dry-run)",
            )

        creds = self.session_store.get_platform_credentials("facebook")
        if not creds.get("configured"):
            return PublishResult(
                success=False,
                platform="facebook",
                error="Facebook credentials (FACEBOOK_PAGE_ACCESS_TOKEN, FACEBOOK_PAGE_ID) not configured.",
            )

        try:
            page_id = creds["page_id"]
            token = creds["page_access_token"]
            url = f"https://graph.facebook.com/v19.0/{page_id}/feed"

            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, data={"message": payload.text, "access_token": token})
                elapsed = round((time.time() - start_time) * 1000, 2)
                if resp.status_code == 200:
                    post_id = resp.json().get("id")
                    return PublishResult(
                        success=True,
                        platform="facebook",
                        post_id=post_id,
                        url=f"https://facebook.com/{post_id}",
                        execution_time_ms=elapsed,
                        tier_used="facebook_graph_api",
                    )
                return PublishResult(
                    success=False,
                    platform="facebook",
                    error=f"Facebook Graph API error: {resp.text}",
                    execution_time_ms=elapsed,
                )
        except Exception as e:
            elapsed = round((time.time() - start_time) * 1000, 2)
            return PublishResult(
                success=False,
                platform="facebook",
                error=f"Exception publishing to Facebook: {e}",
                execution_time_ms=elapsed,
            )
