"""WordPress Adapter for OmniMCP Pro."""

from __future__ import annotations

import base64
import time
from typing import Any, Dict, Optional

import httpx

from src.auth.session_store import SessionStore
from src.core.adapter_base import BasePlatformAdapter, PlatformLimits, PublishPayload, PublishResult
from src.core.transformer import ContentTransformer


class WordPressAdapter(BasePlatformAdapter):
    """Publishes Markdown-rendered semantic HTML to WordPress via WP REST API."""

    def __init__(self, session_store: Optional[SessionStore] = None):
        super().__init__(name="wordpress")
        self.session_store = session_store or SessionStore()

    def get_limits(self) -> PlatformLimits:
        return PlatformLimits(
            name="wordpress",
            max_characters=100000,
            allows_media=True,
            max_media_count=20,
            supports_markdown=True,
            rate_limit_per_day=50,
        )

    async def verify_auth(self) -> Dict[str, Any]:
        creds = self.session_store.get_platform_credentials("wordpress")
        if not creds.get("configured"):
            return {"authenticated": False, "error": "WordPress credentials not configured."}

        url = f"{creds['url'].rstrip('/')}/wp-json/wp/v2/users/me"
        auth_str = f"{creds['username']}:{creds['app_password']}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers={"Authorization": f"Basic {b64_auth}"})
                if resp.status_code == 200:
                    data = resp.json()
                    return {"authenticated": True, "name": data.get("name"), "slug": data.get("slug")}
                return {"authenticated": False, "error": f"HTTP {resp.status_code}: {resp.text[:100]}"}
        except Exception as e:
            return {"authenticated": False, "error": str(e)}

    async def publish(self, payload: PublishPayload) -> PublishResult:
        start_time = time.time()

        transformed = ContentTransformer.transform_wordpress(payload.text, title=payload.title)

        if payload.dry_run:
            elapsed = round((time.time() - start_time) * 1000, 2)
            return PublishResult(
                success=True,
                platform="wordpress",
                post_id="dryrun-wp-101",
                url="https://example.com/blog/dryrun-post",
                execution_time_ms=elapsed,
                tier_used="wp_rest_api (dry-run)",
                warnings=["Simulated dry-run: Markdown rendered to semantic HTML."],
            )

        creds = self.session_store.get_platform_credentials("wordpress")
        if not creds.get("configured"):
            return PublishResult(
                success=False,
                platform="wordpress",
                error="WordPress credentials not configured in .env or cookies.json",
            )

        url = f"{creds['url'].rstrip('/')}/wp-json/wp/v2/posts"
        auth_str = f"{creds['username']}:{creds['app_password']}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()

        wp_payload = {
            "title": payload.title or "New Update",
            "content": transformed.html_body,
            "status": "publish" if payload.confirm_post else "draft",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    url,
                    headers={"Authorization": f"Basic {b64_auth}", "Content-Type": "application/json"},
                    json=wp_payload,
                )
                elapsed = round((time.time() - start_time) * 1000, 2)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    post_id = str(data.get("id"))
                    link = data.get("link")
                    return PublishResult(
                        success=True,
                        platform="wordpress",
                        post_id=post_id,
                        url=link,
                        execution_time_ms=elapsed,
                        tier_used="wp_rest_api",
                    )
                return PublishResult(
                    success=False,
                    platform="wordpress",
                    error=f"WordPress REST error: HTTP {resp.status_code} - {resp.text[:200]}",
                    execution_time_ms=elapsed,
                )
        except Exception as e:
            elapsed = round((time.time() - start_time) * 1000, 2)
            return PublishResult(
                success=False,
                platform="wordpress",
                error=f"Exception publishing to WordPress: {e}",
                execution_time_ms=elapsed,
            )
