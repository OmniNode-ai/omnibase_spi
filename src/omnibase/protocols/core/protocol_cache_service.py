"""
Protocol definitions for cache service abstraction.

Provides cache service protocols that can be implemented by different
cache backends (in-memory, Redis, etc.) and injected via ONEXContainer.
"""

from typing import Any, Optional, Protocol, runtime_checkable

from omnibase.protocols.types.core_types import ContextValue


@runtime_checkable
class ProtocolCacheService(Protocol):
    """Protocol for cache service operations."""

    async def get(self, key: str) -> Optional[dict[str, Any]]:
        """
        Retrieve cached data by key.

        Args:
            key: Cache key to retrieve

        Returns:
            Cached data dictionary, or None if not found or expired
        """
        ...

    async def set(
        self, key: str, value: dict[str, Any], ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        Store data in cache with optional TTL.

        Args:
            key: Cache key to store under
            value: Data to cache
            ttl_seconds: Time to live in seconds, None for default

        Returns:
            True if successfully cached, False otherwise
        """
        ...

    async def delete(self, key: str) -> bool:
        """
        Delete cached data by key.

        Args:
            key: Cache key to delete

        Returns:
            True if key existed and was deleted, False otherwise
        """
        ...

    async def clear(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache entries, optionally by pattern.

        Args:
            pattern: Optional pattern to match keys for deletion

        Returns:
            Number of entries cleared
        """
        ...

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists and is not expired, False otherwise
        """
        ...

    def get_stats(self) -> dict[str, ContextValue]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics (hits, misses, size, etc.)
        """
        ...


@runtime_checkable
class ProtocolCacheServiceProvider(Protocol):
    """Protocol for cache service provider."""

    def create_cache_service(self) -> ProtocolCacheService:
        """
        Create cache service instance.

        Returns:
            ProtocolCacheService implementation
        """
        ...

    def get_cache_configuration(self) -> dict[str, ContextValue]:
        """
        Get cache configuration parameters.

        Returns:
            Dictionary with cache configuration
        """
        ...
