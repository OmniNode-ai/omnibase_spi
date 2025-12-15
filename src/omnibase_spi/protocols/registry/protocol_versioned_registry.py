"""Versioned registry protocol for managing multiple versions of registered items.

This module provides a protocol for registries that need to track multiple versions
of the same key. It extends ProtocolRegistryBase with version-aware operations,
enabling semantic versioning, version querying, and automatic latest-version resolution.

Thread Safety:
    Implementations MUST be thread-safe for concurrent read/write operations across
    different versions of the same key. Callers should not assume thread safety -
    always check implementation docs.

Type Parameters:
    K: Key type (e.g., str, enum, type). Must be hashable.
    V: Value type (e.g., policy class, schema, API handler).

Version Ordering:
    This protocol assumes SEMANTIC VERSIONING (semver) for version ordering:
    - Format: MAJOR.MINOR.PATCH (e.g., "1.2.3")
    - Comparison: Lexicographic on (major, minor, patch) tuple
    - Latest: Highest semantic version (e.g., "2.0.0" > "1.9.9")

    Implementations MAY support alternative versioning schemes (e.g., timestamps,
    monotonic integers) but MUST document their ordering semantics clearly.

Base Method Behavior:
    - `register(key, value)` operates on the LATEST version (or creates "0.0.1" if none)
    - `get(key)` retrieves the LATEST version
    - `unregister(key)` removes ALL versions of the key
    - `list_keys()` returns keys with ANY version registered
    - `is_registered(key)` returns True if ANY version exists

    This design ensures backward compatibility with ProtocolRegistryBase while
    providing version-aware operations via the extended methods.

Usage:
    Use this protocol when:
    - Managing multiple versions of policies, schemas, or APIs
    - Version rollback/pinning is required
    - Migration between versions needs to be tracked
    - Semantic versioning is a domain requirement

    Use ProtocolRegistryBase when:
    - Versioning is not required (single active version per key)
    - Simple key-value mapping is sufficient

Example:
    >>> from omnibase_spi.protocols.registry import ProtocolVersionedRegistry
    >>>
    >>> # Define a versioned policy registry
    >>> registry: ProtocolVersionedRegistry[str, type[Policy]]
    >>>
    >>> # Register multiple versions
    >>> await registry.register_version("rate-limit", "1.0.0", RateLimitV1)
    >>> await registry.register_version("rate-limit", "1.1.0", RateLimitV1_1)
    >>> await registry.register_version("rate-limit", "2.0.0", RateLimitV2)
    >>>
    >>> # Get specific version
    >>> v1 = await registry.get_version("rate-limit", "1.0.0")
    >>>
    >>> # Get latest (returns RateLimitV2 - highest semver)
    >>> latest = await registry.get_latest("rate-limit")
    >>>
    >>> # List all versions for a key
    >>> versions = await registry.list_versions("rate-limit")
    >>> # ["1.0.0", "1.1.0", "2.0.0"]
    >>>
    >>> # Get all versions as mapping
    >>> all_versions = await registry.get_all_versions("rate-limit")
    >>> # {"1.0.0": RateLimitV1, "1.1.0": RateLimitV1_1, "2.0.0": RateLimitV2}
    >>>
    >>> # Base protocol methods work with latest version (sync bridge methods)
    >>> registry.get("rate-limit")  # Returns RateLimitV2 (delegates to get_latest internally)
    >>> registry.is_registered("rate-limit")  # True if ANY version exists

See Also:
    - ProtocolRegistryBase: Base protocol for generic registries
    - ProtocolHandlerRegistry: Specialized registry for protocol handlers
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.registry.protocol_registry_base import (
    K,
    ProtocolRegistryBase,
    V,
)

__all__ = ["ProtocolVersionedRegistry"]


@runtime_checkable
class ProtocolVersionedRegistry(ProtocolRegistryBase[K, V], Protocol):
    """
    Protocol for versioned key-value registry implementations.

    This protocol extends ProtocolRegistryBase with version-aware operations,
    enabling management of multiple versions of the same key using semantic
    versioning for ordering and latest-version resolution.

    Type Parameters:
        K: Key type (must be hashable in concrete implementations)
        V: Value type (can be any type)

    Thread Safety:
        Implementations MUST be thread-safe. Concurrent operations across
        different versions of the same key must not corrupt internal state.
        Use locks, lock-free data structures, or copy-on-write semantics.

    Error Handling:
        - `get_version()` MUST raise KeyError if key or version not found
        - `get_latest()` MUST raise KeyError if key has no versions
        - `register_version()` MAY raise ValueError for duplicate (key, version) pairs
        - `list_versions()` returns empty list for non-existent keys (does not raise)
        - `get_all_versions()` returns empty dict for non-existent keys (does not raise)

    Async/Sync Design Pattern:
        Version-specific methods (register_version, get_version, get_latest,
        list_versions, get_all_versions) are async to support I/O operations such as:
        - Loading versioned data from external storage (databases, caches)
        - Querying remote registries or distributed systems
        - Event notification and audit logging
        - Distributed locking and coordination

        Base protocol methods (register, get, list_keys, is_registered, unregister)
        are inherited as synchronous from ProtocolRegistryBase for backward compatibility.

        IMPORTANT - Implementation Guidance:
        Implementations MUST internally bridge the sync/async boundary by having sync
        base methods delegate to async version methods. Three strategies are available:

        1. Event Loop Strategy - Running async operations in sync context:
           ```python
           import asyncio

           def get(self, key: K) -> V:
               # Option A: Use existing event loop if available
               try:
                   loop = asyncio.get_running_loop()
                   raise RuntimeError("Cannot use sync method from async context")
               except RuntimeError:
                   # No running loop - safe to create new one
                   return asyncio.run(self.get_latest(key))
           ```

           Reference: https://docs.python.org/3/library/asyncio-runner.html#asyncio.run

           WARNING: This strategy can deadlock if called from an async context.
           Always check for running event loop first. For production code, prefer
           Strategy 2 or 3.

        2. Cached Sync View Strategy - Maintain dual data structures:
           ```python
           class VersionedRegistry:
               def __init__(self):
                   self._async_store: dict[K, dict[str, V]] = {}  # Authoritative
                   self._sync_cache: dict[K, V] = {}  # Latest versions only
                   self._cache_lock = threading.Lock()

               async def register_version(self, key: K, version: str, value: V) -> None:
                   self._async_store.setdefault(key, {})[version] = value
                   latest = max(self._async_store[key].keys())  # Semver ordering
                   with self._cache_lock:
                       self._sync_cache[key] = self._async_store[key][latest]

               def get(self, key: K) -> V:
                   # Fast sync access to cached latest version
                   with self._cache_lock:
                       return self._sync_cache[key]
           ```

           Reference: Python threading.Lock - https://docs.python.org/3/library/threading.html#lock-objects

           BENEFITS: No event loop overhead, safe from async context, fast reads.
           TRADEOFFS: Memory overhead (2x storage), cache invalidation complexity.

        3. Thread-Safe Blocking Wrapper Strategy - Use concurrent.futures:
           ```python
           import asyncio
           from concurrent.futures import ThreadPoolExecutor

           class VersionedRegistry:
               def __init__(self):
                   self._executor = ThreadPoolExecutor(max_workers=1)
                   self._loop = asyncio.new_event_loop()
                   self._executor.submit(self._loop.run_forever)

               def get(self, key: K) -> V:
                   # Submit async operation to dedicated event loop thread
                   future = asyncio.run_coroutine_threadsafe(
                       self.get_latest(key),
                       self._loop
                   )
                   return future.result()  # Blocks until complete
           ```

           Reference: https://docs.python.org/3/library/asyncio-task.html#asyncio.run_coroutine_threadsafe

           BENEFITS: Safe from any context, clean separation of concerns.
           TRADEOFFS: Thread overhead, complexity managing event loop lifecycle.

        Strategy Selection Guide:
            - Strategy 1: Simple cases, CLI tools, scripts (not production services)
            - Strategy 2: High-read, low-write workloads with memory to spare
            - Strategy 3: Production services requiring robust sync/async bridging

        No concrete implementation exists yet in omnibase_infra - these are reference
        patterns for implementers to follow. Future versions will provide reference
        implementations once versioned registry use cases emerge.

    Invariants:
        - After `await register_version(k, v, val)`, `await get_version(k, v)` returns `val`
        - `await get_latest(k)` returns the version with highest semantic version number
        - `await list_versions(k)` returns versions in ascending semver order
        - `unregister(k)` removes ALL versions of key `k` (sync wrapper around async operation)
        - `is_registered(k)` returns True if ANY version of `k` exists (sync wrapper around async operation)
        - `get(k)` returns same value as `await get_latest(k)` (sync wrapper delegates to async)

    Version Ordering:
        Implementations MUST use semantic versioning (MAJOR.MINOR.PATCH) by default.
        Alternative schemes (timestamps, integers) MAY be supported but MUST be
        documented clearly in implementation docstrings.

    Semantic Version Validation:
        Version strings MUST follow semantic versioning format: MAJOR.MINOR.PATCH
        where each component is a non-negative integer with no leading zeros (except "0").

        Valid examples:
            - "1.0.0", "2.1.3", "10.20.30", "0.0.1"

        Invalid examples:
            - "1.0" (missing PATCH)
            - "v1.0.0" (prefix not allowed)
            - "1.0.0-beta" (pre-release identifiers not supported)
            - "01.0.0" (leading zeros not allowed)
            - "latest" (not a valid semver)

        Implementations MUST validate version strings before storage and MUST
        raise ValueError for invalid formats.

        Reference: https://semver.org (strict MAJOR.MINOR.PATCH subset)

        Recommended validation pattern:
            ```python
            import re

            def _validate_semver(version: str) -> bool:
                '''Validate strict semantic version format (MAJOR.MINOR.PATCH).

                Returns:
                    True if version matches format, False otherwise.
                '''
                # Pattern: non-negative integers, no leading zeros (except "0")
                pattern = r'^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)$'
                return bool(re.match(pattern, version))

            # Usage in register_version:
            if not _validate_semver(version):
                raise ValueError(
                    f"Invalid semantic version format: {version!r}. "
                    f"Expected MAJOR.MINOR.PATCH (e.g., '1.0.0')"
                )
            ```
    """

    async def register_version(self, key: K, version: str, value: V) -> None:
        """
        Register a specific version of a key-value pair.

        Adds or updates a versioned mapping. Multiple versions of the same key
        can coexist. Behavior for duplicate (key, version) pairs is implementation-
        specific (may overwrite or raise ValueError).

        This method is async to support I/O operations such as persisting version
        metadata to external storage, event notification, or distributed locking.

        Args:
            key: Registration key (must be hashable).
            version: Semantic version string in MAJOR.MINOR.PATCH format (e.g., "1.2.3").
                    Implementations MUST validate format before storage.
            value: Value to associate with this (key, version) pair.

        Raises:
            ValueError: If duplicate (key, version) and implementation forbids overwrites,
                       or if version string is invalid (e.g., not valid semver format).
            RegistryError: If registration fails due to internal error.

        Thread Safety:
            Must be safe to call concurrently with other registry methods, including
            other `register_version()` calls for different versions of the same key.

        Example:
            >>> await registry.register_version("api", "1.0.0", ApiV1Handler)
            >>> await registry.register_version("api", "2.0.0", ApiV2Handler)
            >>> # Now two versions coexist
        """
        ...

    async def get_version(self, key: K, version: str) -> V:
        """
        Retrieve a specific version of a registered value.

        This method is async to support I/O operations such as loading versioned
        data from external storage, remote registries, or cache systems.

        Args:
            key: Registration key to lookup.
            version: Semantic version string to retrieve.

        Returns:
            Value associated with the (key, version) pair.

        Raises:
            KeyError: If key is not registered or version does not exist.
            RegistryError: If retrieval fails due to internal error.

        Thread Safety:
            Must be safe to call concurrently with register_version/unregister.

        Example:
            >>> handler_v1 = await registry.get_version("api", "1.0.0")
            >>> handler_v2 = await registry.get_version("api", "2.0.0")
        """
        ...

    async def get_latest(self, key: K) -> V:
        """
        Retrieve the latest version of a registered value.

        The "latest" version is determined by semantic versioning ordering
        (highest MAJOR.MINOR.PATCH wins). If multiple versions exist with
        same semver, behavior is implementation-specific.

        This method is async to support I/O operations such as querying version
        metadata from external storage or distributed registries.

        Args:
            key: Registration key to lookup.

        Returns:
            Value associated with the latest version of the key.

        Raises:
            KeyError: If key has no registered versions.
            RegistryError: If retrieval fails due to internal error.

        Thread Safety:
            Result is a point-in-time snapshot. A newer version may be registered
            immediately after this call returns.

        Example:
            >>> await registry.register_version("api", "1.0.0", ApiV1)
            >>> await registry.register_version("api", "2.0.0", ApiV2)
            >>> latest = await registry.get_latest("api")  # Returns ApiV2
        """
        ...

    async def list_versions(self, key: K) -> list[str]:
        """
        List all registered versions for a key.

        Returns versions in ascending semantic version order (e.g., "1.0.0"
        before "2.0.0"). Returns empty list if key has no versions.

        This method is async to support I/O operations such as querying version
        lists from external registries or database indexes.

        Args:
            key: Key to list versions for.

        Returns:
            List of version strings in ascending semver order.
            Empty list if key not registered.

        Thread Safety:
            Must return a consistent snapshot. Concurrent version registrations
            during list construction must not cause corruption or exceptions.

        Example:
            >>> await registry.register_version("api", "1.0.0", ApiV1)
            >>> await registry.register_version("api", "2.0.0", ApiV2)
            >>> await registry.register_version("api", "1.5.0", ApiV1_5)
            >>> versions = await registry.list_versions("api")
            >>> # ["1.0.0", "1.5.0", "2.0.0"]
        """
        ...

    async def get_all_versions(self, key: K) -> dict[str, V]:
        """
        Retrieve all versions of a registered key as a mapping.

        Returns a dictionary mapping version strings to their corresponding
        values. Useful for migration, rollback, or version comparison scenarios.

        This method is async to support I/O operations such as bulk loading
        versioned data from external storage or distributed caches.

        Args:
            key: Registration key to retrieve all versions for.

        Returns:
            Dictionary mapping version strings to values.
            Empty dict if key not registered.
            Order of dict items is implementation-specific (may be insertion order).

        Thread Safety:
            Must return a consistent snapshot. Concurrent version registrations
            during retrieval must not cause corruption or exceptions.

        Example:
            >>> await registry.register_version("policy", "1.0.0", PolicyV1)
            >>> await registry.register_version("policy", "2.0.0", PolicyV2)
            >>> all_versions = await registry.get_all_versions("policy")
            >>> # {"1.0.0": PolicyV1, "2.0.0": PolicyV2}
            >>>
            >>> # Migrate all policies
            >>> for version, policy_cls in all_versions.items():
            ...     await migrate_policy(version, policy_cls)
        """
        ...
