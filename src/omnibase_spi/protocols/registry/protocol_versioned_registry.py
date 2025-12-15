"""Versioned registry protocol for managing multiple versions of registered items.

This module provides a protocol for registries that need to track multiple versions
of the same key. It provides version-aware async operations, enabling semantic
versioning, version querying, and automatic latest-version resolution.

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

Design Rationale - Independent Async Protocol:
    ProtocolVersionedRegistry does NOT inherit from ProtocolRegistryBase due to
    fundamental async/sync incompatibility:

    1. Async-First Design:
       - ALL methods are async to support I/O operations (database queries,
         distributed registries, remote version lookups, event notifications)
       - Async methods cannot override sync methods without breaking Liskov
         Substitution Principle (LSP)
       - Async context is necessary for version-aware operations that may involve
         external storage systems

    2. Semantic Differences:
       - ProtocolRegistryBase assumes single-value-per-key semantics
       - ProtocolVersionedRegistry requires multi-value-per-key semantics
       - Version resolution adds complexity that doesn't fit base protocol model

    3. Benefits of Independence:
       - Clean async interface throughout the protocol (no sync/async mixing)
       - Freedom to evolve versioned registry semantics without impacting base protocol
       - Explicit opt-in to versioning complexity (not hidden behind inheritance)
       - Type checker can properly validate async context propagation

    4. Implementation Pattern:
       - Implementations SHOULD provide both sync base protocol methods AND async
         versioned methods to support dual-mode access when needed
       - Delegation pattern: sync methods can delegate to async methods via
         asyncio.run() or event loop integration
       - Pure async implementations can focus solely on versioned protocol

Base Method Behavior:
    All methods are async and version-aware:
    - `await register(key, value)` operates on the LATEST version (or creates "0.0.1" if none)
    - `await get(key)` retrieves the LATEST version
    - `await unregister(key)` removes ALL versions of the key
    - `await list_keys()` returns keys with ANY version registered
    - `await is_registered(key)` returns True if ANY version exists

    This design provides a clean async interface for version-aware registry operations.

Usage:
    Use this protocol when:
    - Managing multiple versions of policies, schemas, or APIs
    - Version rollback/pinning is required
    - Migration between versions needs to be tracked
    - Semantic versioning is a domain requirement
    - Async I/O operations are needed (database, remote registry, event bus)

    Use ProtocolRegistryBase when:
    - Versioning is not required (single active version per key)
    - Simple key-value mapping is sufficient
    - Synchronous operations are preferred (in-memory registry)

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
    >>> # Base protocol methods work with latest version (async overrides)
    >>> await registry.get("rate-limit")  # Returns RateLimitV2 (delegates to get_latest internally)
    >>> await registry.is_registered("rate-limit")  # True if ANY version exists

See Also:
    - ProtocolRegistryBase: Base protocol for generic registries
    - ProtocolHandlerRegistry: Specialized registry for protocol handlers
"""

from __future__ import annotations

from typing import Generic, Protocol, TypeVar, runtime_checkable

# Type variables for generic versioned registry
K = TypeVar("K")  # Key type (must be hashable in implementations)
V = TypeVar("V")  # Value type

__all__ = ["ProtocolVersionedRegistry"]


@runtime_checkable
class ProtocolVersionedRegistry(Protocol, Generic[K, V]):
    """
    Protocol for versioned key-value registry implementations.

    This protocol provides version-aware registry operations, enabling management
    of multiple versions of the same key using semantic versioning for ordering
    and latest-version resolution. It defines a fully async interface for all
    registry operations.

    .. versionadded:: 0.3.0

    .. versionchanged:: 0.4.0
        Removed inheritance from ProtocolRegistryBase due to async/sync incompatibility.
        All methods are now fully async. This is a breaking change: synchronous
        method calls (e.g., ``registry.get(key)``) must be replaced with async calls
        (``await registry.get(key)``). This change ensures compliance with the
        Liskov Substitution Principle - async methods cannot override sync methods
        without violating LSP. See Migration Guide in docs/api-reference/REGISTRY.md
        for upgrade instructions.

    Type Parameters:
        K: Key type (must be hashable in concrete implementations)
        V: Value type (can be any type)

    Thread Safety:
        Implementations MUST be thread-safe for concurrent read/write operations.
        Concurrent operations across different versions of the same key must not
        corrupt internal state.

        Thread Safety Guarantees:
            - **Consistency Model**: Sequential consistency for single-key operations.
              Each method call appears to execute atomically for its specific key.

            - **Atomic Operations**: Each method call is atomic with respect to its key.
              Operations on different keys may execute concurrently without coordination.

            - **Snapshot Isolation**: list_keys() and get_all_versions() return point-in-time
              snapshots. The returned data reflects a consistent state at some moment during
              execution, though concurrent modifications may occur before/after.

            - **Concurrent Registration**: Multiple threads can register different versions
              of the same key concurrently. Operations MUST serialize to prevent corruption.

            - **Read-Your-Writes**: After successful register_version(), a subsequent
              get_version() for that (key, version) pair MUST return the registered value
              (assuming no intermediate unregister).

            - **No Lost Updates**: Concurrent register_version() calls for the same
              (key, version) pair MUST serialize. The last write wins, or implementation
              MAY raise ValueError to prevent silent overwrites.

        Race Condition Behavior:
            - **Concurrent get_latest() during register_version()**: May return old or
              new version (both valid). Callers should not assume atomicity across multiple
              get_latest() calls for the same key.

            - **Concurrent unregister() during get_version()**: May raise KeyError if the
              unregister completes before get_version acquires its read lock. This is
              expected behavior.

            - **Concurrent list_versions() during register_version()**: Returned list may
              or may not include the newly registered version. Snapshot timing determines
              inclusion.

        Implementation Guidance:
            Implementers should use one of these patterns:

            - **Lock-based**: threading.Lock, threading.RLock, or asyncio.Lock for
              serialization. Suitable for simple in-memory registries.

            - **Lock-free**: Immutable data structures with atomic swap operations
              (e.g., copy-on-write dict with atomic reference replacement). Suitable
              for high-concurrency scenarios.

            - **Copy-on-write**: Snapshot-at-start for consistent reads, with versioned
              internal state. Suitable for distributed or eventually-consistent systems.

        Thread Safety Example (Lock-based):
            ```python
            import asyncio
            import threading

            class ThreadSafeVersionedRegistry:
                def __init__(self):
                    self._store: dict[K, dict[str, V]] = {}
                    self._lock = threading.RLock()

                async def register_version(self, key: K, version: str, value: V) -> None:
                    with self._lock:
                        self._store.setdefault(key, {})[version] = value

                async def get_latest(self, key: K) -> V:
                    with self._lock:
                        if key not in self._store or not self._store[key]:
                            raise KeyError(f"Key not registered: {key}")
                        latest_version = max(self._store[key].keys(), key=self._parse_semver)
                        return self._store[key][latest_version]
            ```

        Caller Guidance (SHOULD):
            - Do NOT assume thread safety without checking implementation documentation
            - Be aware that latest-version lookups are point-in-time snapshots
            - Expect that a newer version may be registered immediately after get_latest()
            - Use application-level locking if transactional semantics are required
            - Consider eventual consistency for distributed registry implementations

    Error Handling:
        - `get_version()` MUST raise KeyError if key or version not found
        - `get_latest()` MUST raise KeyError if key has no versions
        - `register_version()` MAY raise ValueError for duplicate (key, version) pairs
        - `list_versions()` returns empty list for non-existent keys (does not raise)
        - `get_all_versions()` returns empty dict for non-existent keys (does not raise)

    Async Design Pattern:
        ALL methods in this protocol are async to support I/O operations such as:
        - Loading versioned data from external storage (databases, caches)
        - Querying remote registries or distributed systems
        - Event notification and audit logging
        - Distributed locking and coordination

        This protocol defines a fully async interface independent of ProtocolRegistryBase,
        which uses synchronous methods. The async design enables consistent async/await
        patterns throughout the versioned registry implementation.

        IMPORTANT - Implementation Guidance:
        All base protocol methods (register, get, list_keys, is_registered, unregister)
        MUST delegate to their corresponding version-aware async methods:

        - `register(key, value)` → `register_version(key, version, value)`
          (choose appropriate version: "0.0.1" for new keys, or increment latest)
        - `get(key)` → `get_latest(key)`
        - `is_registered(key)` → Check if `list_versions(key)` is non-empty
        - `unregister(key)` → Remove all entries from version storage
        - `list_keys()` → Return unique keys from version storage

        Example implementation pattern:
            ```python
            class VersionedRegistry:
                def __init__(self):
                    self._store: dict[K, dict[str, V]] = {}  # key -> {version -> value}

                async def register_version(self, key: K, version: str, value: V) -> None:
                    if not self._validate_semver(version):
                        raise ValueError(f"Invalid semver: {version}")
                    self._store.setdefault(key, {})[version] = value

                async def get_latest(self, key: K) -> V:
                    if key not in self._store or not self._store[key]:
                        raise KeyError(f"Key not registered: {key}")
                    latest_version = max(self._store[key].keys(), key=self._parse_semver)
                    return self._store[key][latest_version]

                async def register(self, key: K, value: V) -> None:
                    # Delegate to register_version with appropriate version
                    if key in self._store and self._store[key]:
                        # Increment latest version's PATCH component
                        latest = max(self._store[key].keys(), key=self._parse_semver)
                        major, minor, patch = self._parse_semver(latest)
                        new_version = f"{major}.{minor}.{patch + 1}"
                    else:
                        new_version = "0.0.1"
                    await self.register_version(key, new_version, value)

                async def get(self, key: K) -> V:
                    # Delegate to get_latest
                    return await self.get_latest(key)
            ```

        No concrete implementation exists yet in omnibase_infra - this is a reference
        pattern for implementers to follow. Future versions will provide reference
        implementations once versioned registry use cases emerge.

    Invariants:
        - After `await register_version(k, v, val)`, `await get_version(k, v)` returns `val`
        - `await get_latest(k)` returns the version with highest semantic version number
        - `await list_versions(k)` returns versions in ascending semver order
        - `await unregister(k)` removes ALL versions of key `k`
        - `await is_registered(k)` returns True if ANY version of `k` exists
        - `await get(k)` returns same value as `await get_latest(k)` (delegates to get_latest)
        - `await register(k, val)` delegates to `await register_version(k, "0.0.1", val)` or latest version

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

        .. versionadded:: 0.4.0

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

        .. versionadded:: 0.4.0

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

        .. versionadded:: 0.4.0

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

        .. versionadded:: 0.4.0

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

        .. versionadded:: 0.4.0

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

    # ===== Base Registry Methods (Async) =====
    # These methods are DUPLICATED from ProtocolRegistryBase (not inherited) to provide
    # version-aware async implementations. Duplication is intentional due to async/sync
    # incompatibility - async methods cannot override sync methods without breaking LSP.
    #
    # METHOD SELECTION GUIDE:
    #
    # Use register_version() when:
    #   - You need explicit version control (e.g., "1.2.3")
    #   - Multiple versions must coexist simultaneously
    #   - Version pinning/rollback is required
    #   - Migration between specific versions needs tracking
    #   - External version numbering scheme is provided
    #
    # Use register() when:
    #   - You want automatic version management
    #   - Latest version semantics are sufficient
    #   - Simpler API is preferred for basic use cases
    #   - Version numbers are implementation detail
    #   - Migration from ProtocolRegistryBase code
    #
    # Decision Matrix:
    #   ┌─────────────────────────┬───────────────────┬──────────────────────┐
    #   │ Scenario                │ Method            │ Rationale            │
    #   ├─────────────────────────┼───────────────────┼──────────────────────┤
    #   │ API versioning          │ register_version  │ Explicit versions    │
    #   │ Schema evolution        │ register_version  │ Track migrations     │
    #   │ Policy rollback         │ register_version  │ Pin to version       │
    #   │ Simple latest-only      │ register          │ Auto version mgmt    │
    #   │ Single active version   │ register          │ Simpler semantics    │
    #   │ Migration from base     │ register          │ Compatible API       │
    #   └─────────────────────────┴───────────────────┴──────────────────────┘
    #
    # Usage Examples:
    #
    #   # Explicit version control (recommended for production APIs)
    #   await registry.register_version("payment-api", "1.0.0", PaymentV1)
    #   await registry.register_version("payment-api", "2.0.0", PaymentV2)
    #   v1_handler = await registry.get_version("payment-api", "1.0.0")
    #   v2_handler = await registry.get_latest("payment-api")  # Returns PaymentV2
    #
    #   # Automatic version management (simpler for internal use)
    #   await registry.register("cache-policy", CachePolicy)  # Creates v0.0.1
    #   await registry.register("cache-policy", ImprovedCache)  # Creates v0.0.2
    #   latest = await registry.get("cache-policy")  # Returns ImprovedCache

    async def register(self, key: K, value: V) -> None:
        """
        Register a key-value pair in the registry.

        Implementations MUST delegate to register_version with an appropriate
        version:
        - **New key**: Use "0.0.1" as initial version
        - **Existing key**: Increment PATCH component of latest version
          (e.g., 1.2.3 → 1.2.4)

        Version Increment Semantics:
            This method is intended for development/testing scenarios where
            explicit version management is not required. For production use,
            prefer explicit register_version() calls with semantic versions.

            Auto-incrementing PATCH assumes backward-compatible bug fixes.
            Breaking changes or new features should use register_version()
            with appropriate MAJOR/MINOR increments.

        Rapid Calls:
            Multiple rapid register() calls will create version sequence:
            0.0.1 → 0.0.2 → 0.0.3 → ...

            If this is not desired, use register_version() directly to control
            version assignment.

        .. versionadded:: 0.1.0
        .. versionchanged:: 0.4.0
            Changed to async method. Previously synchronous in ProtocolRegistryBase.

        Args:
            key: Registration key (must be hashable).
            value: Value to associate with the key.

        Raises:
            ValueError: If duplicate key and implementation forbids overwrites.
            RegistryError: If registration fails due to internal error.

        Thread Safety:
            Must be safe to call concurrently with other registry methods.

        Example:
            >>> # Development: Quick registration without version control
            >>> await registry.register("api", ApiHandler)
            >>> # Creates version 0.0.1
            >>>
            >>> await registry.register("api", ApiHandlerFixed)
            >>> # Creates version 0.0.2 (patch increment)
            >>>
            >>> # Production: Explicit version control
            >>> await registry.register_version("api", "2.0.0", ApiV2Handler)
            >>> # Explicit semantic version for breaking change
        """
        ...

    async def get(self, key: K) -> V:
        """
        Retrieve the latest version of a registered value.

        Implementations MUST delegate to get_latest internally.

        .. versionadded:: 0.1.0
        .. versionchanged:: 0.4.0
            Changed to async method. Previously synchronous in ProtocolRegistryBase.

        Args:
            key: Registration key to lookup.

        Returns:
            Value associated with the latest version of the key.

        Raises:
            KeyError: If key is not registered.
            RegistryError: If retrieval fails due to internal error.

        Thread Safety:
            Must be safe to call concurrently with register/unregister.

        Example:
            >>> handler = await registry.get("api")
            >>> # Returns latest version (delegates to get_latest internally)
        """
        ...

    async def list_keys(self) -> list[K]:
        """
        List all registered keys.

        Returns keys that have at least one version registered.

        .. versionadded:: 0.1.0
        .. versionchanged:: 0.4.0
            Changed to async method. Previously synchronous in ProtocolRegistryBase.

        Returns:
            List of all registered keys. Empty list if no keys registered.
            Order is implementation-specific (may be insertion order, sorted, etc.).

        Thread Safety:
            Must return a consistent snapshot. Concurrent modifications during
            list construction must not cause corruption or exceptions.

        Example:
            >>> keys = await registry.list_keys()
            >>> for key in keys:
            ...     print(f"{key} -> {await registry.get(key)}")
        """
        ...

    async def is_registered(self, key: K) -> bool:
        """
        Check if a key has any registered versions.

        Returns True if the key has at least one version.

        .. versionadded:: 0.1.0
        .. versionchanged:: 0.4.0
            Changed to async method. Previously synchronous in ProtocolRegistryBase.

        Args:
            key: Key to check.

        Returns:
            True if key has at least one version registered, False otherwise.

        Thread Safety:
            Result is a point-in-time snapshot. Key may be registered/unregistered
            immediately after this call returns.

        Example:
            >>> if await registry.is_registered("api"):
            ...     handler = await registry.get("api")
            ... else:
            ...     print("API not available")
        """
        ...

    async def unregister(self, key: K) -> bool:
        """
        Remove ALL versions of a key from the registry.

        This removes ALL registered versions of the key from the registry.

        Idempotent operation - safe to call multiple times with same key.

        .. versionadded:: 0.1.0
        .. versionchanged:: 0.4.0
            Changed to async method. Previously synchronous in ProtocolRegistryBase.

        Args:
            key: Key to remove (all versions will be deleted).

        Returns:
            True if key was registered and removed (at least one version existed).
            False if key was not registered (no-op).

        Thread Safety:
            Must be safe to call concurrently with other registry methods.
            If multiple threads unregister same key, only one returns True.

        Example:
            >>> if await registry.unregister("api"):
            ...     print("All API versions unregistered")
            ... else:
            ...     print("API was not registered")
        """
        ...
