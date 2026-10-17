"""Platform Adapters Package for OmniMCP Pro."""

from src.auth.session_store import SessionStore
from src.core.registry import PlatformAdapterRegistry, global_adapter_registry

from .facebook.adapter import FacebookAdapter
from .linkedin.adapter import LinkedInAdapter
from .threads.adapter import ThreadsAdapter
from .twitter.adapter import TwitterAdapter
from .wordpress.adapter import WordPressAdapter


def initialize_all_adapters(
    registry: PlatformAdapterRegistry = global_adapter_registry,
    session_store: SessionStore = None,
) -> PlatformAdapterRegistry:
    """Instantiate and register all supported platform adapters."""
    store = session_store or SessionStore()

    registry.register(LinkedInAdapter(session_store=store))
    registry.register(TwitterAdapter(session_store=store))
    registry.register(WordPressAdapter(session_store=store))
    registry.register(ThreadsAdapter(session_store=store))
    registry.register(FacebookAdapter(session_store=store))

    return registry


__all__ = [
    "LinkedInAdapter",
    "TwitterAdapter",
    "WordPressAdapter",
    "ThreadsAdapter",
    "FacebookAdapter",
    "initialize_all_adapters",
]
