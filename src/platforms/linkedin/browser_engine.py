"""Hardened Patchright Browser Engine for LinkedIn (Tier 2).

Strictly used for media/image uploads, deep profile scraping, search,
and fallback when Tier 1 encounters an authentication challenge.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.auth.session_store import SessionStore


class LinkedInBrowserEngine:
    """Automates LinkedIn web interactions via stealth Patchright Chromium."""

    def __init__(self, session_store: Optional[SessionStore] = None):
        self.session_store = session_store or SessionStore()

    async def _setup_authenticated_context(self, playwright_instance, headless: bool = True):
        """Create a browser context pre-loaded with LinkedIn session cookies."""
        session = self.session_store.get_linkedin_session()
        browser = await playwright_instance.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
            ),
        )

        if session:
            cookies = [
                {
                    "name": "li_at",
                    "value": session.li_at,
                    "domain": ".linkedin.com",
                    "path": "/",
                    "httpOnly": True,
                    "secure": True,
                },
                {
                    "name": "JSESSIONID",
                    "value": session.jsessionid,
                    "domain": ".linkedin.com",
                    "path": "/",
                    "httpOnly": False,
                    "secure": True,
                },
            ]
            await context.add_cookies(cookies)

        return browser, context

    async def publish_media_post(
        self,
        text: str,
        media_paths: List[str],
        visibility: str = "PUBLIC",
        headless: bool = True,
    ) -> Tuple[bool, Optional[str], Optional[str], float, Optional[str]]:
        """Upload media files and publish post via Patchright file picker.

        Returns: (success, activity_urn, post_url, elapsed_ms, error)
        """
        from patchright.async_api import async_playwright

        start_time = time.time()
        # Verify media paths exist
        valid_media = []
        for p in media_paths:
            path_obj = Path(p).expanduser().resolve()
            if path_obj.exists() and path_obj.is_file():
                valid_media.append(str(path_obj))
            else:
                return (
                    False,
                    None,
                    None,
                    0.0,
                    f"Media file not found or invalid: {p}",
                )

        try:
            async with async_playwright() as p:
                browser, context = await self._setup_authenticated_context(p, headless=headless)
                page = await context.new_page()

                sys.stderr.write("[BrowserEngine] Navigating to LinkedIn feed...\n")
                await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=25000)

                # Check if logged in
                current_url = page.url
                if "login" in current_url or "checkpoint" in current_url:
                    await browser.close()
                    elapsed = round((time.time() - start_time) * 1000, 2)
                    return (
                        False,
                        None,
                        None,
                        elapsed,
                        "LinkedIn authentication failed: Redirected to login page. Please refresh cookies.",
                    )

                # 1. Trigger "Start a post" modal
                start_post_selectors = [
                    "button.share-box-feed-entry__trigger",
                    "button:has-text('Start a post')",
                    "button[aria-label='Start a post']",
                ]
                post_trigger = None
                for sel in start_post_selectors:
                    try:
                        el = page.locator(sel).first
                        if await el.is_visible(timeout=3000):
                            post_trigger = el
                            break
                    except Exception:
                        continue

                if not post_trigger:
                    await browser.close()
                    elapsed = round((time.time() - start_time) * 1000, 2)
                    return False, None, None, elapsed, "Could not find 'Start a post' button on feed."

                await post_trigger.click()
                await page.wait_for_timeout(1000)

                # 2. File picker for media
                if valid_media:
                    sys.stderr.write(f"[BrowserEngine] Uploading {len(valid_media)} media file(s)...\n")
                    # Try setting files directly on hidden input[type=file]
                    file_input = page.locator('input[type="file"]').first
                    if await file_input.count() > 0:
                        await file_input.set_input_files(valid_media)
                    else:
                        # Intercept file chooser on media button
                        media_btn_selectors = [
                            "button[aria-label='Add media']",
                            "button[aria-label='Add a photo']",
                            "button[aria-label='Media']",
                        ]
                        for m_sel in media_btn_selectors:
                            btn = page.locator(m_sel).first
                            if await btn.is_visible(timeout=2000):
                                async with page.expect_file_chooser() as fc_info:
                                    await btn.click()
                                file_chooser = await fc_info.value
                                await file_chooser.set_files(valid_media)
                                break

                    # Wait for media preview modal and click Next
                    await page.wait_for_timeout(2000)
                    next_btn = page.locator("button:has-text('Next')").first
                    if await next_btn.is_visible(timeout=4000):
                        await next_btn.click()
                        await page.wait_for_timeout(1000)

                # 3. Enter post text into editor
                editor = page.locator("div.editor-content div[role='textbox'], div.ql-editor").first
                if await editor.is_visible(timeout=5000):
                    await editor.click()
                    await editor.fill(text)
                else:
                    # Fallback keyboard typing
                    await page.keyboard.type(text)

                await page.wait_for_timeout(1000)

                # 4. Click Post button
                submit_btn = page.locator("button.share-actions__primary-action, button:has-text('Post')").first
                if await submit_btn.is_enabled(timeout=4000):
                    await submit_btn.click()
                else:
                    await browser.close()
                    elapsed = round((time.time() - start_time) * 1000, 2)
                    return False, None, None, elapsed, "Post button is disabled or not clickable."

                # Wait for post modal to close
                await page.wait_for_timeout(3000)
                await browser.close()

                elapsed_ms = round((time.time() - start_time) * 1000, 2)
                sys.stderr.write(f"[BrowserEngine] Media post published in {elapsed_ms}ms\n")
                return True, "browser_activity_published", "https://www.linkedin.com/feed/", elapsed_ms, None

        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            sys.stderr.write(f"[BrowserEngine] Error during media publish: {e}\n")
            return False, None, None, elapsed_ms, str(e)

    async def scrape_person_profile(self, vanity_name: str, headless: bool = True) -> Dict[str, Any]:
        """Deep scrape of a public/connected profile section (headline, about, experience)."""
        from patchright.async_api import async_playwright

        start_time = time.time()
        url = f"https://www.linkedin.com/in/{vanity_name.strip('/')}/"

        try:
            async with async_playwright() as p:
                browser, context = await self._setup_authenticated_context(p, headless=headless)
                page = await context.new_page()

                await page.goto(url, wait_until="domcontentloaded", timeout=25000)

                # Extract primary details
                name = await page.locator("h1.inline.t-24, h1.text-heading-xlarge").first.inner_text() or ""
                headline = await page.locator("div.text-body-medium.break-words").first.inner_text() or ""
                about = ""
                about_loc = page.locator("section:has-text('About') div.inline-show-more-text").first
                if await about_loc.count() > 0:
                    about = await about_loc.inner_text()

                await browser.close()
                elapsed = round((time.time() - start_time) * 1000, 2)

                return {
                    "success": True,
                    "vanity_name": vanity_name,
                    "name": name.strip(),
                    "headline": headline.strip(),
                    "about": about.strip(),
                    "url": url,
                    "elapsed_ms": elapsed,
                }
        except Exception as e:
            elapsed = round((time.time() - start_time) * 1000, 2)
            return {
                "success": False,
                "vanity_name": vanity_name,
                "error": str(e),
                "elapsed_ms": elapsed,
            }
