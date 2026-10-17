"""Content Transformer for OmniMCP Pro.

Transforms a single master post into platform-tailored payloads:
- LinkedIn: 3000-char cap, link extraction into first comment, fold cutoff calculation.
- X (Twitter): Sentence-aware thread chunking (max 280 chars with 1/n indicators).
- Threads: 500-char cap with clean formatting.
- WordPress: Markdown to semantic HTML conversion.
- Facebook: Clean page post layout.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import markdown


@dataclass
class TransformedContent:
    platform: str
    body: str
    first_comment: Optional[str] = None
    thread_items: List[str] = field(default_factory=list)
    html_body: Optional[str] = None
    character_count: int = 0
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContentTransformer:
    """Transforms raw user or agent content to match individual platform algorithms."""

    URL_REGEX = re.compile(r"https?://[^\s<>\"']+")

    @classmethod
    def extract_urls(cls, text: str) -> List[str]:
        return cls.URL_REGEX.findall(text)

    @classmethod
    def transform_linkedin(cls, text: str, preserve_links_in_body: bool = False) -> TransformedContent:
        """Format for LinkedIn: strip external links to first comment if needed, check fold cutoff."""
        warnings: List[str] = []
        first_comment: Optional[str] = None
        cleaned_text = text

        if not preserve_links_in_body:
            urls = cls.extract_urls(text)
            if urls:
                # Remove URLs from body
                for u in urls:
                    cleaned_text = cleaned_text.replace(u, "").strip()
                # Clean up any dangling double newlines
                cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()
                links_str = " ".join(urls)
                first_comment = f"🔗 Link: {links_str}"
                warnings.append("Extracted external URL(s) to first comment to maximize LinkedIn algorithm reach.")

        # Check character limit (3000 chars)
        if len(cleaned_text) > 3000:
            warnings.append(f"Content exceeds LinkedIn 3000-char limit ({len(cleaned_text)} chars). Will truncate.")
            cleaned_text = cleaned_text[:2997] + "..."

        # Calculate fold cutoff (LinkedIn usually places "...see more" around 140-210 chars or 3-5 lines)
        lines = cleaned_text.splitlines()
        first_fold = "\n".join(lines[:3]) if len(lines) >= 3 else cleaned_text[:140]

        return TransformedContent(
            platform="linkedin",
            body=cleaned_text,
            first_comment=first_comment,
            character_count=len(cleaned_text),
            warnings=warnings,
            metadata={
                "fold_cutoff": first_fold,
                "has_first_comment": first_comment is not None,
            },
        )

    @classmethod
    def transform_twitter(cls, text: str, max_chars: int = 280) -> TransformedContent:
        """Split text into sentence-aware numbered tweet threads (1/n, 2/n)."""
        warnings: List[str] = []

        if len(text) <= max_chars:
            return TransformedContent(
                platform="twitter",
                body=text,
                thread_items=[text],
                character_count=len(text),
                warnings=warnings,
                metadata={"is_thread": False, "thread_count": 1},
            )

        # Content exceeds 280 chars; split into numbered thread
        # 1. Break into paragraph or sentence chunks
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: List[str] = []

        for p in paragraphs:
            if len(p) <= 250:
                chunks.append(p)
            else:
                # Split paragraph by sentences
                sentences = re.split(r"(?<=[.!?])\s+", p)
                current_chunk = ""
                for s in sentences:
                    if len(current_chunk) + len(s) + 1 <= 240:
                        current_chunk = f"{current_chunk} {s}".strip() if current_chunk else s
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = s
                if current_chunk:
                    chunks.append(current_chunk)

        # Append pagination counters (e.g., " (1/4)")
        total_parts = len(chunks)
        thread_items: List[str] = []
        for i, chunk in enumerate(chunks, 1):
            pagination = f" ({i}/{total_parts})"
            # Ensure it fits within 280 chars
            available_len = max_chars - len(pagination)
            if len(chunk) > available_len:
                chunk = chunk[: available_len - 3] + "..."
            thread_items.append(f"{chunk}{pagination}")

        warnings.append(f"Content automatically split into a {len(thread_items)}-part X thread.")

        return TransformedContent(
            platform="twitter",
            body=thread_items[0],
            thread_items=thread_items,
            character_count=len(thread_items[0]),
            warnings=warnings,
            metadata={"is_thread": True, "thread_count": len(thread_items)},
        )

    @classmethod
    def transform_threads(cls, text: str, max_chars: int = 500) -> TransformedContent:
        """Format for Meta Threads (500 char cap)."""
        warnings: List[str] = []
        cleaned = text.strip()
        if len(cleaned) > max_chars:
            warnings.append(f"Content exceeds Threads 500-char limit ({len(cleaned)} chars). Truncating.")
            cleaned = cleaned[: max_chars - 3] + "..."

        return TransformedContent(
            platform="threads",
            body=cleaned,
            character_count=len(cleaned),
            warnings=warnings,
        )

    @classmethod
    def transform_wordpress(cls, markdown_text: str, title: Optional[str] = None) -> TransformedContent:
        """Convert Markdown to semantic HTML for WordPress publishing."""
        html = markdown.markdown(
            markdown_text,
            extensions=["extra", "codehilite", "nl2br"],
        )
        return TransformedContent(
            platform="wordpress",
            body=markdown_text,
            html_body=html,
            character_count=len(markdown_text),
            metadata={"title": title or "New Post"},
        )

    @classmethod
    def transform_facebook(cls, text: str) -> TransformedContent:
        """Format for Facebook Pages."""
        return TransformedContent(
            platform="facebook",
            body=text.strip(),
            character_count=len(text.strip()),
        )

    @classmethod
    def transform_all(cls, text: str, title: Optional[str] = None) -> Dict[str, TransformedContent]:
        """Generate transformed payloads for all 5 platforms at once."""
        return {
            "linkedin": cls.transform_linkedin(text),
            "twitter": cls.transform_twitter(text),
            "threads": cls.transform_threads(text),
            "wordpress": cls.transform_wordpress(text, title=title),
            "facebook": cls.transform_facebook(text),
        }
