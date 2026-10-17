"""LinkedIn OAuth 2.0 Helper for OmniMCP Pro.

Handles Authorization Code flow and token exchange compliant with
LinkedIn Consumer Solutions Platform (OpenID Connect + Share on LinkedIn).
"""

from __future__ import annotations

import os
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from src.auth.session_store import SessionStore


class LinkedInOAuthHelper:
    """Manages LinkedIn 3-legged OAuth 2.0 authorization and token exchange."""

    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    DEFAULT_SCOPES = ["openid", "profile", "email", "w_member_social"]

    def __init__(self, session_store: Optional[SessionStore] = None):
        self.session_store = session_store or SessionStore()

    def get_authorization_url(
        self,
        client_id: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = "omnimcp_pro_auth",
        scopes: Optional[list[str]] = None,
    ) -> str:
        cid = client_id or os.getenv("LINKEDIN_CLIENT_ID")
        if not cid:
            raise ValueError("LINKEDIN_CLIENT_ID is required to generate authorization URL.")

        r_uri = redirect_uri or os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/api/auth/linkedin/callback")
        scope_str = " ".join(scopes or self.DEFAULT_SCOPES)

        params = {
            "response_type": "code",
            "client_id": cid.strip(),
            "redirect_uri": r_uri.strip(),
            "scope": scope_str,
            "state": state,
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    async def exchange_code_for_token(
        self,
        code: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ) -> Dict[str, Any]:
        cid = client_id or os.getenv("LINKEDIN_CLIENT_ID")
        csecret = client_secret or os.getenv("LINKEDIN_CLIENT_SECRET")
        r_uri = redirect_uri or os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/api/auth/linkedin/callback")

        if not cid or not csecret:
            raise ValueError("Both LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET are required.")

        payload = {
            "grant_type": "authorization_code",
            "code": code.strip(),
            "redirect_uri": r_uri.strip(),
            "client_id": cid.strip(),
            "client_secret": csecret.strip(),
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(self.TOKEN_URL, data=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                access_token = data.get("access_token")
                expires_in = data.get("expires_in")
                id_token = data.get("id_token")

                if access_token:
                    self._persist_token_to_env(access_token)
                    return {
                        "success": True,
                        "access_token": access_token,
                        "expires_in": expires_in,
                        "id_token": id_token,
                    }
                return {"success": False, "error": "No access_token in response", "raw": data}

            return {
                "success": False,
                "error": f"LinkedIn token exchange failed (HTTP {resp.status_code}): {resp.text}",
            }

    def _persist_token_to_env(self, access_token: str) -> None:
        """Update .env file and process environment with the fresh access token."""
        os.environ["LINKEDIN_ACCESS_TOKEN"] = access_token
        env_path = Path(__file__).resolve().parent.parent.parent / ".env"
        if not env_path.exists():
            return

        try:
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            updated = False
            new_lines = []
            for line in lines:
                if line.startswith("LINKEDIN_ACCESS_TOKEN="):
                    new_lines.append(f'LINKEDIN_ACCESS_TOKEN="{access_token}"\n')
                    updated = True
                else:
                    new_lines.append(line)

            if not updated:
                new_lines.append(f'LINKEDIN_ACCESS_TOKEN="{access_token}"\n')

            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

        except Exception as e:
            sys.stderr.write(f"[LinkedInOAuthHelper] Error updating .env: {e}\n")
