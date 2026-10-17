"""Official LinkedIn Developer Platform API Client (OAuth 2.0 + REST/UGC).

Compliant with Microsoft Learn / LinkedIn Developer Documentation:
- Endpoint: POST https://api.linkedin.com/v2/ugcPosts
- Media Register: POST https://api.linkedin.com/v2/assets?action=registerUpload
- Authentication: 3-legged OAuth 2.0 Bearer Token (w_member_social scope)
"""

from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)


class OfficialLinkedInClient:
    """Official LinkedIn API client using OAuth 2.0 Bearer tokens and UGC/REST endpoints."""

    UGC_POST_URL = "https://api.linkedin.com/v2/ugcPosts"
    ASSETS_REGISTER_URL = "https://api.linkedin.com/v2/assets?action=registerUpload"
    USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
    ME_URL = "https://api.linkedin.com/v2/me"

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or os.getenv("LINKEDIN_ACCESS_TOKEN")

    def is_configured(self) -> bool:
        return bool(self.access_token and self.access_token.strip())

    def _get_headers(self) -> Dict[str, str]:
        token = (self.access_token or "").strip()
        return {
            "Authorization": f"Bearer {token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def get_current_member(self) -> Dict[str, Any]:
        """Fetch member identity via official OpenID Connect userinfo or /v2/me."""
        if not self.is_configured():
            return {"authenticated": False, "error": "No LINKEDIN_ACCESS_TOKEN configured"}

        headers = self._get_headers()
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # 1. Try modern OIDC userinfo
                resp = await client.get(self.USERINFO_URL, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    sub = data.get("sub", "")
                    return {
                        "authenticated": True,
                        "person_urn": f"urn:li:person:{sub}" if sub else None,
                        "name": data.get("name", ""),
                        "given_name": data.get("given_name", ""),
                        "family_name": data.get("family_name", ""),
                        "email": data.get("email", ""),
                        "picture": data.get("picture", ""),
                    }

                # 2. Try legacy /v2/me
                resp_me = await client.get(self.ME_URL, headers=headers)
                if resp_me.status_code == 200:
                    me_data = resp_me.json()
                    member_id = me_data.get("id", "")
                    first_name = me_data.get("localizedFirstName", "")
                    last_name = me_data.get("localizedLastName", "")
                    return {
                        "authenticated": True,
                        "person_urn": f"urn:li:person:{member_id}" if member_id else None,
                        "name": f"{first_name} {last_name}".strip(),
                    }

                return {
                    "authenticated": False,
                    "error": f"Official LinkedIn OAuth authentication failed (HTTP {resp.status_code}): {resp.text}",
                }
            except Exception as e:
                return {"authenticated": False, "error": f"Exception checking official LinkedIn OAuth: {e}"}

    async def create_official_text_post(
        self,
        text: str,
        author_urn: Optional[str] = None,
        visibility: str = "PUBLIC",
    ) -> Tuple[bool, Optional[str], Optional[str], float, Optional[str]]:
        """Publish post using official LinkedIn UGC Post API.

        Headers:
            Authorization: Bearer <access_token>
            X-Restli-Protocol-Version: 2.0.0
        """
        if not self.is_configured():
            return False, None, None, 0.0, "LINKEDIN_ACCESS_TOKEN is not configured in .env"

        start_time = time.time()
        headers = self._get_headers()

        # If author_urn is not supplied, fetch it from authenticated member
        if not author_urn:
            member = await self.get_current_member()
            author_urn = member.get("person_urn")
            if not author_urn:
                return False, None, None, 0.0, f"Could not determine author URN: {member.get('error')}"

        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC" if visibility.upper() == "PUBLIC" else "CONNECTIONS"
            },
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(self.UGC_POST_URL, headers=headers, json=payload)
                elapsed_ms = round((time.time() - start_time) * 1000, 2)

                if resp.status_code in (200, 201):
                    data = resp.json() if resp.content else {}
                    post_id = resp.headers.get("x-restli-id") or data.get("id")
                    post_url = f"https://www.linkedin.com/feed/update/{post_id}/" if post_id else None
                    sys.stderr.write(f"[OfficialLinkedInClient] Published post via official API in {elapsed_ms}ms: {post_id}\n")
                    return True, post_id, post_url, elapsed_ms, None

                return (
                    False,
                    None,
                    None,
                    elapsed_ms,
                    f"Official LinkedIn API error (HTTP {resp.status_code}): {resp.text}",
                )
            except Exception as e:
                elapsed_ms = round((time.time() - start_time) * 1000, 2)
                return False, None, None, elapsed_ms, f"Exception calling official LinkedIn UGC API: {e}"

    async def upload_image_and_create_post(
        self,
        text: str,
        image_path: str,
        author_urn: Optional[str] = None,
        visibility: str = "PUBLIC",
    ) -> Tuple[bool, Optional[str], Optional[str], float, Optional[str]]:
        """3-step Official Media Share flow per Microsoft Learn documentation:
        1. Register upload: POST https://api.linkedin.com/v2/assets?action=registerUpload
        2. Binary upload: PUT/POST to uploadUrl
        3. Create Share with shareMediaCategory: IMAGE and asset URN
        """
        if not self.is_configured():
            return False, None, None, 0.0, "LINKEDIN_ACCESS_TOKEN is not configured in .env"

        img = Path(image_path).expanduser().resolve()
        if not img.exists():
            return False, None, None, 0.0, f"Image file not found: {image_path}"

        start_time = time.time()
        headers = self._get_headers()

        # Step 0: Ensure author URN
        if not author_urn:
            member = await self.get_current_member()
            author_urn = member.get("person_urn")
            if not author_urn:
                return False, None, None, 0.0, f"Could not determine author URN: {member.get('error')}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Step 1: Register Upload
                reg_payload = {
                    "registerUploadRequest": {
                        "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                        "owner": author_urn,
                        "serviceRelationships": [
                            {
                                "relationshipType": "OWNER",
                                "identifier": "urn:li:userGeneratedContent",
                            }
                        ],
                    }
                }

                reg_resp = await client.post(self.ASSETS_REGISTER_URL, headers=headers, json=reg_payload)
                if reg_resp.status_code not in (200, 201):
                    return False, None, None, 0.0, f"Failed to register upload (HTTP {reg_resp.status_code}): {reg_resp.text}"

                reg_data = reg_resp.json().get("value", {})
                upload_url = (
                    reg_data.get("uploadMechanism", {})
                    .get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {})
                    .get("uploadUrl")
                )
                asset_urn = reg_data.get("asset")

                if not upload_url or not asset_urn:
                    return False, None, None, 0.0, f"Invalid registerUpload response: {reg_data}"

                # Step 2: Upload Binary Image
                with open(img, "rb") as f:
                    img_bytes = f.read()

                upload_headers = {"Authorization": f"Bearer {self.access_token}"}
                upload_resp = await client.post(upload_url, headers=upload_headers, content=img_bytes)
                if upload_resp.status_code not in (200, 201):
                    # Some endpoints use PUT
                    upload_resp = await client.put(upload_url, headers=upload_headers, content=img_bytes)

                if upload_resp.status_code not in (200, 201):
                    return False, None, None, 0.0, f"Failed to upload image binary (HTTP {upload_resp.status_code})"

                # Step 3: Create Image Post
                post_payload = {
                    "author": author_urn,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": text},
                            "shareMediaCategory": "IMAGE",
                            "media": [
                                {
                                    "status": "READY",
                                    "media": asset_urn,
                                }
                            ],
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC" if visibility.upper() == "PUBLIC" else "CONNECTIONS"
                    },
                }

                post_resp = await client.post(self.UGC_POST_URL, headers=headers, json=post_payload)
                elapsed_ms = round((time.time() - start_time) * 1000, 2)

                if post_resp.status_code in (200, 201):
                    post_id = post_resp.headers.get("x-restli-id") or post_resp.json().get("id")
                    post_url = f"https://www.linkedin.com/feed/update/{post_id}/" if post_id else None
                    sys.stderr.write(f"[OfficialLinkedInClient] Published image post via official API in {elapsed_ms}ms: {post_id}\n")
                    return True, post_id, post_url, elapsed_ms, None

                return False, None, None, elapsed_ms, f"Failed to publish media post (HTTP {post_resp.status_code}): {post_resp.text}"

            except Exception as e:
                elapsed_ms = round((time.time() - start_time) * 1000, 2)
                return False, None, None, elapsed_ms, f"Exception in official LinkedIn media post: {e}"
