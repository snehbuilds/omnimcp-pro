"""Platform Adapter Registry for OmniMCP Pro.

Coordinates dynamic adapter discovery, registration, and multi-platform broadcasting.
"""

from __future__ import annotations

import sys
import time
from typing import Any, Dict, List, Optional

from .adapter_base import BasePlatformAdapter, PublishPayload, PublishResult
from .safety import SafetyGuard, global_safety_guard
from .transformer import ContentTransformer


class PlatformAdapterRegistry:
    """Central registry and dispatch hub for all platform adapters."""

    def __init__(self, safety_guard: Optional[SafetyGuard] = None):
        self._adapters: Dict[str, BasePlatformAdapter] = {}
        self.safety_guard = safety_guard or global_safety_guard

    def register(self, adapter: BasePlatformAdapter) -> None:
        name = adapter.name.lower().strip()
        self._adapters[name] = adapter
        sys.stderr.write(f"[Registry] Registered adapter for platform: {name}\n")

    def get(self, platform: str) -> Optional[BasePlatformAdapter]:
        return self._adapters.get(platform.lower().strip())

    def list_platforms(self) -> List[str]:
        return sorted(list(self._adapters.keys()))

    async def verify_all(self) -> Dict[str, Any]:
        """Verify authentication status across all registered adapters."""
        results = {}
        for name, adapter in self._adapters.items():
            try:
                auth_info = await adapter.verify_auth()
                results[name] = auth_info
            except Exception as e:
                results[name] = {"authenticated": False, "error": str(e)}
        return results

    def preview_broadcast(
        self,
        text: str,
        targets: Optional[List[str]] = None,
        title: Optional[str] = None,
        media_paths: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate dry-run previews across selected platforms."""
        selected = targets or self.list_platforms()
        previews = {}

        for p_name in selected:
            p_name = p_name.lower().strip()
            adapter = self.get(p_name)
            if not adapter:
                previews[p_name] = {"error": f"Adapter for {p_name} not registered"}
                continue

            # Transform content appropriately
            if p_name == "linkedin":
                transformed = ContentTransformer.transform_linkedin(text)
                payload = PublishPayload(
                    text=transformed.body,
                    first_comment=transformed.first_comment,
                    media_paths=media_paths or [],
                    dry_run=True,
                )
            elif p_name in ("twitter", "x"):
                transformed = ContentTransformer.transform_twitter(text)
                payload = PublishPayload(
                    text=transformed.body,
                    media_paths=media_paths or [],
                    extra={"thread_items": transformed.thread_items},
                    dry_run=True,
                )
            elif p_name == "wordpress":
                transformed = ContentTransformer.transform_wordpress(text, title=title)
                payload = PublishPayload(
                    text=transformed.body,
                    title=title,
                    extra={"html": transformed.html_body},
                    dry_run=True,
                )
            else:
                payload = PublishPayload(text=text, media_paths=media_paths or [], dry_run=True)

            preview_data = adapter.preview(payload)
            previews[p_name] = preview_data

        return {
            "targets": selected,
            "original_length": len(text),
            "media_count": len(media_paths or []),
            "previews": previews,
        }

    async def broadcast_post(
        self,
        text: str,
        targets: Optional[List[str]] = None,
        title: Optional[str] = None,
        media_paths: Optional[List[str]] = None,
        confirm_post: bool = False,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Broadcast a post across specified platforms with SafetyGuard and WriteGate checks."""
        start_time = time.time()
        selected = targets or ["linkedin"]
        results: Dict[str, Any] = {}

        # Evaluate Write Gate
        is_dry_run, write_gate_reason = self.safety_guard.should_dry_run(
            confirm_post=confirm_post,
            requested_dry_run=dry_run,
        )

        for p_name in selected:
            p_name = p_name.lower().strip()
            adapter = self.get(p_name)
            if not adapter:
                results[p_name] = PublishResult(
                    success=False,
                    platform=p_name,
                    error=f"No adapter registered for platform: {p_name}",
                )
                continue

            # Check SafetyGuard if doing live execution
            if not is_dry_run:
                can_post, reason = self.safety_guard.check_can_post_live(p_name)
                if not can_post:
                    results[p_name] = PublishResult(
                        success=False,
                        platform=p_name,
                        error=reason,
                    )
                    continue

                # Inject human jitter delay before live publish
                await self.safety_guard.inject_human_jitter()

            # Transform content based on platform
            if p_name == "linkedin":
                transformed = ContentTransformer.transform_linkedin(text)
                payload = PublishPayload(
                    text=transformed.body,
                    first_comment=transformed.first_comment,
                    media_paths=media_paths or [],
                    dry_run=is_dry_run,
                    confirm_post=confirm_post,
                )
            elif p_name in ("twitter", "x"):
                transformed = ContentTransformer.transform_twitter(text)
                payload = PublishPayload(
                    text=transformed.body,
                    media_paths=media_paths or [],
                    extra={"thread_items": transformed.thread_items},
                    dry_run=is_dry_run,
                    confirm_post=confirm_post,
                )
            elif p_name == "wordpress":
                transformed = ContentTransformer.transform_wordpress(text, title=title)
                payload = PublishPayload(
                    text=transformed.body,
                    title=title,
                    extra={"html": transformed.html_body},
                    dry_run=is_dry_run,
                    confirm_post=confirm_post,
                )
            else:
                payload = PublishPayload(
                    text=text,
                    media_paths=media_paths or [],
                    dry_run=is_dry_run,
                    confirm_post=confirm_post,
                )

            # Execute publish
            try:
                res = await adapter.publish(payload)
                results[p_name] = res

                # Record in SafetyGuard
                self.safety_guard.record_post(platform=p_name, post_id=res.post_id, dry_run=is_dry_run)
            except Exception as e:
                results[p_name] = PublishResult(
                    success=False,
                    platform=p_name,
                    error=f"Unhandled exception in {p_name} publish: {e}",
                )

        total_elapsed = round((time.time() - start_time) * 1000, 2)
        success_count = sum(1 for r in results.values() if r.success)

        return {
            "dry_run": is_dry_run,
            "write_gate_note": write_gate_reason,
            "total_targets": len(selected),
            "successful_targets": success_count,
            "elapsed_ms": total_elapsed,
            "results": {k: v.__dict__ for k, v in results.items()},
        }


# Global default registry instance
global_adapter_registry = PlatformAdapterRegistry()
