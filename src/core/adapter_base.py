"""Base Platform Adapter Interface for OmniMCP Pro.

Defines the contract all social network adapters must implement.
Encapsulates platform limits, payload structure, and standardized result formats.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PlatformLimits:
    """Publishing constraints for a specific social network."""

    name: str
    max_characters: int
    allows_media: bool = True
    max_media_count: int = 1
    supported_media_types: List[str] = field(default_factory=lambda: ["image/jpeg", "image/png", "image/webp"])
    supports_markdown: bool = False
    supports_threads: bool = False
    rate_limit_per_day: int = 10


@dataclass
class PublishPayload:
    """The canonical post payload passed to adapters."""

    text: str
    media_paths: List[str] = field(default_factory=list)
    title: Optional[str] = None
    visibility: str = "PUBLIC"
    first_comment: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dry_run: bool = False
    confirm_post: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PublishResult:
    """Standardized response from any publishing operation."""

    success: bool
    platform: str
    post_id: Optional[str] = None
    url: Optional[str] = None
    execution_time_ms: float = 0.0
    tier_used: str = "default"  # e.g., "voyager_rest", "patchright_browser", "rest_api"
    first_comment_id: Optional[str] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    raw_response: Optional[Dict[str, Any]] = None


class BasePlatformAdapter(ABC):
    """Abstract base class for all platform adapters."""

    def __init__(self, name: str):
        self.name = name.lower().strip()

    @abstractmethod
    def get_limits(self) -> PlatformLimits:
        """Return the rate limits and content constraints for this platform."""
        pass

    @abstractmethod
    async def verify_auth(self) -> Dict[str, Any]:
        """Verify credential validity and return identity information."""
        pass

    @abstractmethod
    async def publish(self, payload: PublishPayload) -> PublishResult:
        """Publish the payload to the external platform."""
        pass

    def preview(self, payload: PublishPayload) -> Dict[str, Any]:
        """Return a structured preview of how the post will appear on this platform."""
        return {
            "platform": self.name,
            "text": payload.text,
            "char_count": len(payload.text),
            "media_count": len(payload.media_paths),
            "first_comment": payload.first_comment,
        }
