"""Twitter/X Adapter for OmniMCP Pro."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from src.auth.session_store import SessionStore
from src.core.adapter_base import BasePlatformAdapter, PlatformLimits, PublishPayload, PublishResult
from src.core.transformer import ContentTransformer


class TwitterAdapter(BasePlatformAdapter):
    """Adapter for X (Twitter) supporting single tweets and multi-part threads."""

    def __init__(self, session_store: Optional[SessionStore] = None):
        super().__init__(name="twitter")
        self.session_store = session_store or SessionStore()

    def get_limits(self) -> PlatformLimits:
        return PlatformLimits(
            name="twitter",
            max_characters=280,
            allows_media=True,
            max_media_count=4,
            supports_threads=True,
            rate_limit_per_day=50,
        )

    async def verify_auth(self) -> Dict[str, Any]:
        creds = self.session_store.get_platform_credentials("twitter")
        return {
            "authenticated": creds.get("configured", False),
            "masked_key": creds.get("masked_api_key"),
        }

    async def publish(self, payload: PublishPayload) -> PublishResult:
        start_time = time.time()

        # Handle Dry-Run Mode
        if payload.dry_run:
            transformed = ContentTransformer.transform_twitter(payload.text)
            thread_count = len(transformed.thread_items)
            elapsed = round((time.time() - start_time) * 1000, 2)
            return PublishResult(
                success=True,
                platform="twitter",
                post_id="dryrun-tweet-id-12345",
                url="https://x.com/user/status/1234567890",
                execution_time_ms=elapsed,
                tier_used="twitter_api_v2 (dry-run)",
                warnings=[f"Simulated dry-run: {thread_count}-part thread previewed."],
            )

        creds = self.session_store.get_platform_credentials("twitter")
        if not creds.get("configured"):
            return PublishResult(
                success=False,
                platform="twitter",
                error="Twitter API credentials (TWITTER_API_KEY, TWITTER_ACCESS_TOKEN) not configured.",
            )

        # In production, execute against Twitter v2 /2/tweets endpoint
        # For now, if keys are set, dispatch authenticated request
        try:
            from authlib.integrations.httpx_client import OAuth1Client

            # Setup OAuth1
            auth = OAuth1Client(
                client_id=creds["api_key"],
                client_secret=creds["api_secret"],
                token=creds["access_token"],
                token_secret=creds["access_token_secret"],
            )

            transformed = ContentTransformer.transform_twitter(payload.text)
            prev_tweet_id = None
            first_tweet_id = None

            async with auth:
                for tweet_text in transformed.thread_items:
                    body: Dict[str, Any] = {"text": tweet_text}
                    if prev_tweet_id:
                        body["reply"] = {"in_reply_to_tweet_id": prev_tweet_id}

                    resp = await auth.post("https://api.twitter.com/2/tweets", json=body)
                    if resp.status_code in (200, 201):
                        data = resp.json().get("data", {})
                        tid = data.get("id")
                        if not first_tweet_id:
                            first_tweet_id = tid
                        prev_tweet_id = tid
                    else:
                        elapsed = round((time.time() - start_time) * 1000, 2)
                        return PublishResult(
                            success=False,
                            platform="twitter",
                            error=f"Twitter API error: HTTP {resp.status_code} - {resp.text}",
                            execution_time_ms=elapsed,
                        )

            elapsed = round((time.time() - start_time) * 1000, 2)
            return PublishResult(
                success=True,
                platform="twitter",
                post_id=first_tweet_id,
                url=f"https://x.com/i/status/{first_tweet_id}" if first_tweet_id else None,
                execution_time_ms=elapsed,
                tier_used="twitter_api_v2",
            )
        except Exception as e:
            elapsed = round((time.time() - start_time) * 1000, 2)
            return PublishResult(
                success=False,
                platform="twitter",
                error=f"Failed to publish to Twitter: {e}",
                execution_time_ms=elapsed,
            )
