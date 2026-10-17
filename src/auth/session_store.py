"""Session and Credential Store for OmniMCP Pro.

Manages persistent session tokens (li_at, JSESSIONID/csrf-token) and API keys.
Stores cookies locally in ~/.omnimcp/cookies.json or loads them from .env.
Ensures tokens are never logged or exposed in plaintext.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Load local environment if available
load_dotenv()


def mask_token(token: Optional[str]) -> str:
    """Safely mask a credential or token for logs and agent UI output."""
    if not token:
        return "[NOT SET]"
    token_str = str(token).strip()
    if len(token_str) <= 8:
        return "****"
    return f"{token_str[:4]}...{token_str[-4:]}"


@dataclass
class LinkedInSession:
    li_at: str
    jsessionid: str

    @property
    def csrf_token(self) -> str:
        """Strip enclosing quotes from JSESSIONID to construct the csrf-token header."""
        return self.jsessionid.strip('"').strip("'")

    @property
    def masked_li_at(self) -> str:
        return mask_token(self.li_at)

    @property
    def masked_jsessionid(self) -> str:
        return mask_token(self.jsessionid)


class SessionStore:
    """Manages credentials across all supported platforms."""

    DEFAULT_DIR = Path.home() / ".omnimcp"
    COOKIE_FILE = DEFAULT_DIR / "cookies.json"

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or self.DEFAULT_DIR
        self.cookie_file = self.storage_dir / "cookies.json"
        self._ensure_storage_dir()

    def _ensure_storage_dir(self) -> None:
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            sys.stderr.write(f"[SessionStore] Warning: Could not create {self.storage_dir}: {e}\n")

    def _load_cookie_file(self) -> Dict[str, Any]:
        if not self.cookie_file.exists():
            return {}
        try:
            with open(self.cookie_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            sys.stderr.write(f"[SessionStore] Failed to read {self.cookie_file}: {e}\n")
            return {}

    def _save_cookie_file(self, data: Dict[str, Any]) -> None:
        try:
            self._ensure_storage_dir()
            with open(self.cookie_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.chmod(self.cookie_file, 0o600)
        except Exception as e:
            sys.stderr.write(f"[SessionStore] Failed to write {self.cookie_file}: {e}\n")

    def get_linkedin_session(self) -> Optional[LinkedInSession]:
        """Fetch LinkedIn session from environment or persistent file store."""
        # 1. Check environment variables
        li_at = os.getenv("LINKEDIN_LI_AT") or os.getenv("LI_AT")
        jsessionid = os.getenv("LINKEDIN_JSESSIONID") or os.getenv("JSESSIONID")

        if li_at and jsessionid:
            return LinkedInSession(li_at=li_at.strip(), jsessionid=jsessionid.strip())

        # 2. Check ~/.omnimcp/cookies.json
        data = self._load_cookie_file()
        li_data = data.get("linkedin", {})
        file_li_at = li_data.get("li_at") or data.get("li_at")
        file_jsessionid = li_data.get("jsessionid") or data.get("jsessionid") or data.get("JSESSIONID")

        if file_li_at and file_jsessionid:
            return LinkedInSession(li_at=str(file_li_at).strip(), jsessionid=str(file_jsessionid).strip())

        return None

    def save_linkedin_session(self, li_at: str, jsessionid: str) -> None:
        """Persist LinkedIn session cookies to the local JSON store."""
        data = self._load_cookie_file()
        data["linkedin"] = {
            "li_at": li_at.strip(),
            "jsessionid": jsessionid.strip(),
        }
        self._save_cookie_file(data)

    def get_platform_credentials(self, platform: str) -> Dict[str, Any]:
        """Retrieve credentials for any supported platform from env or cookie store."""
        platform = platform.lower().strip()
        data = self._load_cookie_file()
        platform_data = data.get(platform, {})

        if platform == "linkedin":
            sess = self.get_linkedin_session()
            if sess:
                return {
                    "configured": True,
                    "li_at": sess.li_at,
                    "jsessionid": sess.jsessionid,
                    "masked_li_at": sess.masked_li_at,
                    "masked_jsessionid": sess.masked_jsessionid,
                }
            return {"configured": False}

        elif platform in ("twitter", "x"):
            api_key = os.getenv("TWITTER_API_KEY") or platform_data.get("api_key")
            api_secret = os.getenv("TWITTER_API_SECRET") or platform_data.get("api_secret")
            access_token = os.getenv("TWITTER_ACCESS_TOKEN") or platform_data.get("access_token")
            access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET") or platform_data.get("access_token_secret")
            configured = bool(api_key and api_secret and access_token and access_token_secret)
            return {
                "configured": configured,
                "api_key": api_key,
                "api_secret": api_secret,
                "access_token": access_token,
                "access_token_secret": access_token_secret,
                "masked_api_key": mask_token(api_key),
            }

        elif platform == "wordpress":
            url = os.getenv("WORDPRESS_URL") or platform_data.get("url")
            username = os.getenv("WORDPRESS_USERNAME") or platform_data.get("username")
            app_password = os.getenv("WORDPRESS_APP_PASSWORD") or platform_data.get("app_password")
            configured = bool(url and username and app_password)
            return {
                "configured": configured,
                "url": url,
                "username": username,
                "app_password": app_password,
                "masked_password": mask_token(app_password),
            }

        elif platform == "threads":
            token = os.getenv("THREADS_ACCESS_TOKEN") or platform_data.get("access_token")
            user_id = os.getenv("THREADS_USER_ID") or platform_data.get("user_id")
            configured = bool(token and user_id)
            return {
                "configured": configured,
                "access_token": token,
                "user_id": user_id,
                "masked_token": mask_token(token),
            }

        elif platform == "facebook":
            token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN") or platform_data.get("page_access_token")
            page_id = os.getenv("FACEBOOK_PAGE_ID") or platform_data.get("page_id")
            configured = bool(token and page_id)
            return {
                "configured": configured,
                "page_access_token": token,
                "page_id": page_id,
                "masked_token": mask_token(token),
            }

        return {"configured": False}

    def get_all_platforms_status(self) -> Dict[str, Dict[str, Any]]:
        """Return a summary of configuration status across all platforms for the UI HUD."""
        platforms = ["linkedin", "twitter", "wordpress", "threads", "facebook"]
        status = {}
        for p in platforms:
            creds = self.get_platform_credentials(p)
            status[p] = {
                "name": p.title() if p != "wordpress" else "WordPress",
                "configured": creds.get("configured", False),
            }
        return status
