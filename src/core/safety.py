"""Strict Anti-Ban Safety Guard & Write Gate for OmniMCP Pro.

Enforces:
1. 180s (3-minute) minimum cooldown between live publishing actions.
2. Daily ceiling of 6 posts/day on LinkedIn (configurable per platform).
3. Human jitter delays (randomized 1.5s to 3.5s) on live operations.
4. Write Gate: Requires confirm_post=True AND OMNI_WRITE_ENABLED=true.
"""

from __future__ import annotations

import asyncio
import os
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional, Tuple


@dataclass
class PostRecord:
    timestamp: float
    platform: str
    post_id: Optional[str] = None
    dry_run: bool = False


@dataclass
class SafetyStatus:
    cooldown_seconds: int
    cooldown_remaining_seconds: float
    is_on_cooldown: bool
    daily_limit: int
    posts_today: int
    can_post_live: bool
    write_enabled_in_env: bool
    reason: Optional[str] = None


class SafetyGuard:
    """Singleton-style or injected guard ensuring no robotic or rapid-fire publishing."""

    COOLDOWN_SECONDS: int = 180  # 3 minutes
    DAILY_LIMIT_LINKEDIN: int = 6

    def __init__(self, cooldown_seconds: int = 180, daily_limit: int = 6):
        self.cooldown_seconds = cooldown_seconds
        self.daily_limit = daily_limit
        self._history: List[PostRecord] = []
        self._last_live_post_time: float = 0.0

    @property
    def write_enabled_in_env(self) -> bool:
        """Check if environment explicitly authorizes live mutations."""
        val = os.getenv("OMNI_WRITE_ENABLED", "").lower().strip()
        return val in ("true", "1", "yes", "on")

    def should_dry_run(self, confirm_post: bool, requested_dry_run: bool) -> Tuple[bool, Optional[str]]:
        """Evaluate the Write Gate. Returns (is_dry_run, reason_if_forced)."""
        if requested_dry_run:
            return True, "Dry-run requested by user/agent."

        if not confirm_post:
            return True, "Write Gate: 'confirm_post' is False. Running preview mode."

        if not self.write_enabled_in_env:
            return (
                True,
                "Write Gate: OMNI_WRITE_ENABLED is not set to 'true' in .env. Running preview mode.",
            )

        return False, None

    def check_can_post_live(self, platform: str = "linkedin") -> Tuple[bool, Optional[str]]:
        """Check whether a live post is currently permitted under anti-ban rules."""
        now = time.time()
        elapsed = now - self._last_live_post_time

        # 1. Cooldown check
        if self._last_live_post_time > 0 and elapsed < self.cooldown_seconds:
            remaining = int(self.cooldown_seconds - elapsed)
            return False, f"Anti-Ban Guard: Active cooldown. Please wait {remaining} seconds before posting again."

        # 2. Daily frequency check
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        live_posts_today = sum(
            1 for p in self._history if not p.dry_run and p.platform.lower() == platform.lower() and p.timestamp >= today_start
        )

        limit = self.daily_limit if platform.lower() == "linkedin" else 15
        if live_posts_today >= limit:
            return (
                False,
                f"Anti-Ban Guard: Daily limit of {limit} posts reached for {platform.title()} today ({live_posts_today}/{limit}).",
            )

        return True, None

    async def inject_human_jitter(self, min_sec: float = 1.5, max_sec: float = 3.5) -> float:
        """Sleep for a randomized duration to simulate human typing and dispatch rhythms."""
        delay = round(random.uniform(min_sec, max_sec), 2)
        sys.stderr.write(f"[SafetyGuard] Injecting {delay}s human jitter delay...\n")
        await asyncio.sleep(delay)
        return delay

    def record_post(self, platform: str, post_id: Optional[str] = None, dry_run: bool = False) -> None:
        """Log a post occurrence to update cooldown and daily tallies."""
        now = time.time()
        record = PostRecord(timestamp=now, platform=platform, post_id=post_id, dry_run=dry_run)
        self._history.append(record)

        if not dry_run:
            self._last_live_post_time = now

    def get_status(self, platform: str = "linkedin") -> SafetyStatus:
        """Retrieve live metrics for dashboard gauges and countdown timers."""
        now = time.time()
        elapsed = now - self._last_live_post_time
        remaining = max(0.0, self.cooldown_seconds - elapsed) if self._last_live_post_time > 0 else 0.0
        is_on_cooldown = remaining > 0

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        live_posts_today = sum(
            1 for p in self._history if not p.dry_run and p.platform.lower() == platform.lower() and p.timestamp >= today_start
        )

        can_post, reason = self.check_can_post_live(platform)

        return SafetyStatus(
            cooldown_seconds=self.cooldown_seconds,
            cooldown_remaining_seconds=round(remaining, 1),
            is_on_cooldown=is_on_cooldown,
            daily_limit=self.daily_limit,
            posts_today=live_posts_today,
            can_post_live=can_post,
            write_enabled_in_env=self.write_enabled_in_env,
            reason=reason,
        )


# Global default guard instance
global_safety_guard = SafetyGuard()
