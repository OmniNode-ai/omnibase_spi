"""
Protocol definitions for cache service abstraction.

Provides cache service protocols that can be implemented by different
cache backends (in-memory, Redis, etc.) and injected via ONEXContainer.
"""

from typing import (
    TYPE_CHECKING,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from omnibase_spi.protocols.types.core_types import ContextValue

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.core_types import ProtocolCacheStatistics

# Type variable for generic cache values
T = TypeVar("T")


@runtime_checkable
class ProtocolCacheService(Protocol, Generic[T]):
    """
    Protocol for cache service operations.

    Generic cache service supporting any serializable value type.
    Implementations can use in-memory, Redis, or other cache backends.

    Example:
        ```python
        # String cache
        cache: ProtocolCacheService[str] = get_string_cache()
        await cache.set("user:123", "john_doe", ttl_seconds=3600)
        username = await cache.get("user:123")  # Returns Optional[str]

        # Dict cache for complex data
        cache: ProtocolCacheService[dict[str, Any]] = get_dict_cache()
        user_data = {"id": 123, "name": "John", "active": True}
        await cache.set("user:123:profile", user_data, ttl_seconds=1800)

        # Cache operations
        exists = await cache.exists("user:123")
        await cache.delete("user:123")
        await cache.clear()  # Clear all cached data
        ```
    """

    async def get(self, key: str) -> Optional[T]:
        """
        Retrieve cached data by key.

        Args:
            key: Cache key to retrieve

        Returns:
            Cached data, or None if not found or expired
        """
        ...

    async def set(self, key: str, value: T, ttl_seconds: Optional[int] = None) -> bool:
        """
        Store data in cache with optional TTL.

        Args:
            key: Cache key to store under
            value: Data to cache (must be serializable)
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

    def get_stats(self) -> "ProtocolCacheStatistics":
        """
        Get cache statistics.

        Returns:
            Structured cache statistics with hit ratios, memory usage, etc.
        """
        ...


@runtime_checkable
class ProtocolCacheServiceProvider(Protocol, Generic[T]):
    """Protocol for cache service provider."""

    def create_cache_service(self) -> ProtocolCacheService[T]:
        """
        Create cache service instance.

        Returns:
            ProtocolCacheService implementation for type T
        """
        ...

    def get_cache_configuration(self) -> dict[str, ContextValue]:
        """
        Get cache configuration parameters.

        Returns:
            Dictionary with cache configuration
        """
        ...
