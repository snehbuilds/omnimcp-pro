"""Chrome Cookie Refresher for OmniMCP Pro.

Extracts fresh session tokens (li_at, JSESSIONID) from the local Google Chrome profile
or launches a temporary Patchright context to refresh authentication.
"""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Dict, Optional

from .session_store import SessionStore, mask_token


class ChromeCookieRefresher:
    """Extracts or refreshes browser cookies for LinkedIn and other social platforms."""

    def __init__(self, session_store: Optional[SessionStore] = None):
        self.session_store = session_store or SessionStore()

    @staticmethod
    def get_chrome_cookie_path() -> Optional[Path]:
        """Locate the default Chrome Cookies SQLite database across macOS, Linux, and Windows."""
        system = platform.system()
        home = Path.home()

        if system == "Darwin":  # macOS
            path = home / "Library/Application Support/Google/Chrome/Default/Cookies"
            if path.exists():
                return path
            # Check Profile 1 if Default doesn't exist
            alt_path = home / "Library/Application Support/Google/Chrome/Profile 1/Cookies"
            if alt_path.exists():
                return alt_path

        elif system == "Linux":
            path = home / ".config/google-chrome/Default/Cookies"
            if path.exists():
                return path

        elif system == "Windows":
            appdata = os.getenv("LOCALAPPDATA")
            if appdata:
                path = Path(appdata) / "Google/Chrome/User Data/Default/Network/Cookies"
                if path.exists():
                    return path

        return None

    async def refresh_linkedin_via_browser(self, headless: bool = False) -> Dict[str, str]:
        """Launch Patchright browser to obtain active LinkedIn session cookies."""
        try:
            from patchright.async_api import async_playwright

            async with async_playwright() as p:
                sys.stderr.write("[CookieRefresher] Launching Patchright to inspect LinkedIn session...\n")
                browser = await p.chromium.launch(headless=headless)
                context = await browser.new_context()
                page = await context.new_page()

                await page.goto("https://www.linkedin.com/feed/", timeout=15000)
                cookies = await context.cookies(["https://www.linkedin.com"])
                await browser.close()

                li_at = None
                jsessionid = None
                for c in cookies:
                    if c["name"] == "li_at":
                        li_at = c["value"]
                    elif c["name"] == "JSESSIONID":
                        jsessionid = c["value"]

                if li_at and jsessionid:
                    self.session_store.save_linkedin_session(li_at, jsessionid)
                    sys.stderr.write(
                        f"[CookieRefresher] Successfully captured fresh cookies: "
                        f"li_at={mask_token(li_at)}, JSESSIONID={mask_token(jsessionid)}\n"
                    )
                    return {
                        "status": "success",
                        "li_at": li_at,
                        "jsessionid": jsessionid,
                        "masked_li_at": mask_token(li_at),
                        "masked_jsessionid": mask_token(jsessionid),
                    }
                else:
                    return {
                        "status": "unauthenticated",
                        "error": "LinkedIn feed opened, but user is not logged in. Please log in first.",
                    }

        except Exception as e:
            sys.stderr.write(f"[CookieRefresher] Browser refresh error: {e}\n")
            return {
                "status": "error",
                "error": str(e),
            }

    def manual_update(self, li_at: str, jsessionid: str) -> Dict[str, str]:
        """Update session cookies directly from the Web Command Center UI."""
        clean_li_at = li_at.strip()
        clean_jsessionid = jsessionid.strip()
        self.session_store.save_linkedin_session(clean_li_at, clean_jsessionid)
        return {
            "status": "success",
            "masked_li_at": mask_token(clean_li_at),
            "masked_jsessionid": mask_token(clean_jsessionid),
        }
