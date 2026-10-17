"""High-Speed LinkedIn Voyager REST Client (Tier 1).

Executes text-only posts, comment link drops, and profile checks in <500ms
without launching a headless browser.
"""

from __future__ import annotations

import sys
import time
from typing import Any, Dict, Optional, Tuple

import httpx

from src.auth.session_store import LinkedInSession, SessionStore


class LinkedInRestClient:
    """Sub-second Voyager API client using authenticated session cookies."""

    BASE_URL = "https://www.linkedin.com"
    VOYAGER_ME = f"{BASE_URL}/voyager/api/me"
    VOYAGER_NORMANDY = f"{BASE_URL}/voyager/api/contentcreation/normandyShares"
    VOYAGER_UGC = f"{BASE_URL}/voyager/api/ugcPosts"

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    )

    def __init__(self, session_store: Optional[SessionStore] = None):
        self.session_store = session_store or SessionStore()

    def _get_headers(self, session: LinkedInSession) -> Dict[str, str]:
        return {
            "authority": "www.linkedin.com",
            "accept": "application/vnd.linkedin.normalized+json+2.1",
            "accept-language": "en-US,en;q=0.9",
            "csrf-token": session.csrf_token,
            "x-restli-protocol-version": "2.0.0",
            "x-li-lang": "en_US",
            "x-li-track": '{"clientVersion":"1.13.123"}',
            "user-agent": self.DEFAULT_USER_AGENT,
            "cookie": f'li_at={session.li_at}; JSESSIONID="{session.csrf_token}"',
            "content-type": "application/json; charset=UTF-8",
        }

    async def get_current_user(self) -> Dict[str, Any]:
        """Fetch profile identity and verify session validity via /voyager/api/me (<300ms)."""
        session = self.session_store.get_linkedin_session()
        if not session:
            return {"authenticated": False, "error": "No LinkedIn session configured in .env or cookies.json"}

        start_time = time.time()
        headers = self._get_headers(session)

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(self.VOYAGER_ME, headers=headers)
                elapsed_ms = round((time.time() - start_time) * 1000, 2)

                if resp.status_code == 200:
                    data = resp.json()
                    mini_profile = data.get("miniProfile", {})
                    first_name = mini_profile.get("firstName", "")
                    last_name = mini_profile.get("lastName", "")
                    headline = mini_profile.get("occupation", "")
                    vanity_name = mini_profile.get("publicIdentifier", "")
                    urn = mini_profile.get("entityUrn", "")

                    return {
                        "authenticated": True,
                        "first_name": first_name,
                        "last_name": last_name,
                        "name": f"{first_name} {last_name}".strip(),
                        "headline": headline,
                        "vanity_name": vanity_name,
                        "profile_urn": urn,
                        "profile_url": f"https://www.linkedin.com/in/{vanity_name}" if vanity_name else None,
                        "response_time_ms": elapsed_ms,
                    }
                elif resp.status_code in (401, 403):
                    return {
                        "authenticated": False,
                        "error": f"LinkedIn session expired or unauthorized (HTTP {resp.status_code}). Please refresh cookies.",
                        "response_time_ms": elapsed_ms,
                    }
                else:
                    return {
                        "authenticated": False,
                        "error": f"Unexpected response from LinkedIn /voyager/api/me: HTTP {resp.status_code}",
                        "response_time_ms": elapsed_ms,
                    }
            except Exception as e:
                return {
                    "authenticated": False,
                    "error": f"Network exception checking LinkedIn session: {e}",
                    "response_time_ms": round((time.time() - start_time) * 1000, 2),
                }

    async def create_text_post(
        self,
        text: str,
        visibility: str = "PUBLIC",
    ) -> Tuple[bool, Optional[str], Optional[str], float, Optional[str]]:
        """Publish a text post via Voyager /normandyShares or UGC fallback (<500ms).

        Returns: (success, activity_urn, post_url, elapsed_ms, error)
        """
        session = self.session_store.get_linkedin_session()
        if not session:
            return False, None, None, 0.0, "Missing LinkedIn session credentials."

        start_time = time.time()
        headers = self._get_headers(session)

        # 1. Primary endpoint: Normandy Shares
        payload = {
            "visibleToConnectionsOnly": (visibility != "PUBLIC"),
            "commentary": text,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(self.VOYAGER_NORMANDY, headers=headers, json=payload)
                elapsed_ms = round((time.time() - start_time) * 1000, 2)

                if resp.status_code in (200, 201):
                    data = resp.json()
                    activity_urn = data.get("activity") or data.get("urn") or data.get("value", {}).get("activity")
                    post_url = f"https://www.linkedin.com/feed/update/{activity_urn}/" if activity_urn else None
                    sys.stderr.write(f"[LinkedInRestClient] Normandy post successful in {elapsed_ms}ms: {activity_urn}\n")
                    return True, activity_urn, post_url, elapsed_ms, None

                # 2. Fallback: UGC Posts endpoint
                sys.stderr.write(f"[LinkedInRestClient] Normandy returned {resp.status_code}, trying UGC fallback...\n")
                user_info = await self.get_current_user()
                profile_urn = user_info.get("profile_urn", "")

                ugc_payload = {
                    "author": profile_urn,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": text},
                            "shareMediaCategory": "NONE",
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC" if visibility == "PUBLIC" else "CONNECTIONS"
                    },
                }

                resp_ugc = await client.post(self.VOYAGER_UGC, headers=headers, json=ugc_payload)
                elapsed_ms = round((time.time() - start_time) * 1000, 2)

                if resp_ugc.status_code in (200, 201):
                    data_ugc = resp_ugc.json()
                    ugc_urn = data_ugc.get("id") or data_ugc.get("urn")
                    post_url = f"https://www.linkedin.com/feed/update/{ugc_urn}/" if ugc_urn else None
                    return True, ugc_urn, post_url, elapsed_ms, None

                return (
                    False,
                    None,
                    None,
                    elapsed_ms,
                    f"LinkedIn REST failed (Normandy: HTTP {resp.status_code}, UGC: HTTP {resp_ugc.status_code}): {resp.text[:200]}",
                )

            except Exception as e:
                elapsed_ms = round((time.time() - start_time) * 1000, 2)
                return False, None, None, elapsed_ms, f"Network exception in LinkedIn REST post: {e}"

    async def create_comment(self, activity_urn: str, comment_text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Publish a comment on a LinkedIn post for fast first-comment link drops."""
        session = self.session_store.get_linkedin_session()
        if not session:
            return False, None, "Missing LinkedIn session"

        headers = self._get_headers(session)
        # Normalize URN
        urn_clean = activity_urn
        if not urn_clean.startswith("urn:li:"):
            urn_clean = f"urn:li:activity:{urn_clean}"

        comment_url = f"{self.BASE_URL}/voyager/api/feed/comments"
        payload = {
            "objectUrn": urn_clean,
            "commentary": comment_text,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.post(comment_url, headers=headers, json=payload)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    comment_urn = data.get("urn") or data.get("value", {}).get("urn")
                    return True, comment_urn, None
                return False, None, f"Failed to post comment: HTTP {resp.status_code}"
            except Exception as e:
                return False, None, str(e)
