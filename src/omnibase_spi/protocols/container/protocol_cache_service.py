"""
Protocol definitions for cache service abstraction.

Provides cache service protocols that can be implemented by different
cache backends (in-memory, Redis, etc.) and injected via ONEXContainer.
"""

from typing import TYPE_CHECKING, Generic, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ContextValue,
        ProtocolCacheStatistics,
    )

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
        cache: "ProtocolCacheService"[str] = get_string_cache()
        await cache.set("user:123", "john_doe", ttl_seconds=3600)
        username = await cache.get("user:123")  # Returns str | None

        # Dict cache for complex data
        cache: "ProtocolCacheService"[dict[str, "ContextValue"]] = get_dict_cache()
        user_data = {"id": 123, "name": "John", "active": True}
        await cache.set("user:123:profile", user_data, ttl_seconds=1800)

        # Cache operations
        exists = await cache.exists("user:123")
        await cache.delete("user:123")
        await cache.clear()  # Clear all cached data
        ```
    """

    async def get(self, key: str) -> T | None: ...

    async def set(self, key: str, value: T, ttl_seconds: int | None = None) -> bool: ...

    async def delete(self, key: str) -> bool: ...

    async def clear(self, pattern: str | None = None) -> int: ...

    async def exists(self, key: str) -> bool: ...

    async def get_stats(self) -> "ProtocolCacheStatistics": ...


@runtime_checkable
class ProtocolCacheServiceProvider(Protocol, Generic[T]):
    """
    Protocol for cache service provider.

    Defines the factory interface for creating and configuring cache service
    instances. This protocol enables dependency injection and configuration
    management for cache services across the ONEX ecosystem.

    The provider pattern allows for dynamic cache service creation with
    environment-specific configurations and backend selection.

    Methods:
        create_cache_service: Create a new cache service instance with current configuration
        get_cache_configuration: Retrieve current configuration settings

    Example:
        ```python
        @runtime_checkable
        class RedisCacheProviderImpl:
            async def create_cache_service(self) -> ProtocolCacheService[str]:
                # Create Redis-backed cache service
                return RedisCacheService(host="localhost", port=6379)

            async def get_cache_configuration(self) -> dict[str, "ContextValue"]:
                return {
                    "backend": "redis",
                    "host": "localhost",
                    "port": 6379,
                    "max_connections": 10,
                    "default_ttl": 3600
                }

        # Usage in dependency injection
        provider: ProtocolCacheServiceProvider[str] = RedisCacheProviderImpl()
        cache_service = await provider.create_cache_service()
        config = await provider.get_cache_configuration()
        ```

    Type Parameters:
        T: The type of values stored in the cache service instances

    Configuration Management:
        The provider handles configuration loading, validation, and
        environment-specific settings for cache service instances.
    """

    async def create_cache_service(self) -> ProtocolCacheService[T]: ...

    async def get_cache_configuration(self) -> dict[str, "ContextValue"]: ...
