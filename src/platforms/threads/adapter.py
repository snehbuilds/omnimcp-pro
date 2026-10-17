"""Meta Threads Adapter for OmniMCP Pro."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx

from src.auth.session_store import SessionStore
from src.core.adapter_base import BasePlatformAdapter, PlatformLimits, PublishPayload, PublishResult
from src.core.transformer import ContentTransformer


class ThreadsAdapter(BasePlatformAdapter):
    """Publishes updates to Meta Threads via the Threads Graph API."""

    def __init__(self, session_store: Optional[SessionStore] = None):
        super().__init__(name="threads")
        self.session_store = session_store or SessionStore()

    def get_limits(self) -> PlatformLimits:
        return PlatformLimits(
            name="threads",
            max_characters=500,
            allows_media=True,
            max_media_count=10,
            rate_limit_per_day=50,
        )

    async def verify_auth(self) -> Dict[str, Any]:
        creds = self.session_store.get_platform_credentials("threads")
        return {"authenticated": creds.get("configured", False)}

    async def publish(self, payload: PublishPayload) -> PublishResult:
        start_time = time.time()
        transformed = ContentTransformer.transform_threads(payload.text)

        if payload.dry_run:
            elapsed = round((time.time() - start_time) * 1000, 2)
            return PublishResult(
                success=True,
                platform="threads",
                post_id="dryrun-threads-post-1",
                url="https://threads.net/@user/post/preview",
                execution_time_ms=elapsed,
                tier_used="threads_graph_api (dry-run)",
                warnings=["Simulated dry-run: 500-character cap enforced."],
            )

        creds = self.session_store.get_platform_credentials("threads")
        if not creds.get("configured"):
            return PublishResult(
                success=False,
                platform="threads",
                error="Threads credentials (THREADS_ACCESS_TOKEN, THREADS_USER_ID) not configured.",
            )

        # Meta Threads 2-step publish: Create Container -> Publish Container
        try:
            user_id = creds["user_id"]
            token = creds["access_token"]
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Step 1: Create container
                c_url = f"https://graph.threads.net/v1.0/{user_id}/threads"
                c_resp = await client.post(
                    c_url,
                    params={
                        "media_type": "TEXT",
                        "text": transformed.body,
                        "access_token": token,
                    },
                )
                if c_resp.status_code != 200:
                    elapsed = round((time.time() - start_time) * 1000, 2)
                    return PublishResult(
                        success=False,
                        platform="threads",
                        error=f"Failed to create Threads container: {c_resp.text}",
                        execution_time_ms=elapsed,
                    )

                container_id = c_resp.json().get("id")

                # Step 2: Publish container
                p_url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
                p_resp = await client.post(
                    p_url,
                    params={
                        "creation_id": container_id,
                        "access_token": token,
                    },
                )
                elapsed = round((time.time() - start_time) * 1000, 2)
                if p_resp.status_code == 200:
                    post_id = p_resp.json().get("id")
                    return PublishResult(
                        success=True,
                        platform="threads",
                        post_id=post_id,
                        url=f"https://threads.net/post/{post_id}",
                        execution_time_ms=elapsed,
                        tier_used="threads_graph_api",
                    )
                return PublishResult(
                    success=False,
                    platform="threads",
                    error=f"Failed to publish Threads container: {p_resp.text}",
                    execution_time_ms=elapsed,
                )
        except Exception as e:
            elapsed = round((time.time() - start_time) * 1000, 2)
            return PublishResult(
                success=False,
                platform="threads",
                error=f"Exception publishing to Threads: {e}",
                execution_time_ms=elapsed,
            )
