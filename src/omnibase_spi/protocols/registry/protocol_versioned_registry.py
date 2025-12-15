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
    >>> registry.register_version("rate-limit", "1.0.0", RateLimitV1)
    >>> registry.register_version("rate-limit", "1.1.0", RateLimitV1_1)
    >>> registry.register_version("rate-limit", "2.0.0", RateLimitV2)
    >>>
    >>> # Get specific version
    >>> v1 = registry.get_version("rate-limit", "1.0.0")
    >>>
    >>> # Get latest (returns RateLimitV2 - highest semver)
    >>> latest = registry.get_latest("rate-limit")
    >>>
    >>> # List all versions for a key
    >>> versions = registry.list_versions("rate-limit")
    >>> # ["1.0.0", "1.1.0", "2.0.0"]
    >>>
    >>> # Get all versions as mapping
    >>> all_versions = registry.get_all_versions("rate-limit")
    >>> # {"1.0.0": RateLimitV1, "1.1.0": RateLimitV1_1, "2.0.0": RateLimitV2}
    >>>
    >>> # Base protocol methods work with latest version
    >>> registry.get("rate-limit")  # Returns RateLimitV2
    >>> registry.is_registered("rate-limit")  # True if ANY version exists

See Also:
    - ProtocolRegistryBase: Base protocol for generic registries
    - ProtocolHandlerRegistry: Specialized registry for protocol handlers
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.registry.protocol_registry_base import (
    K, ProtocolRegistryBase, V)


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

    Invariants:
        - After `register_version(k, v, val)`, `get_version(k, v)` returns `val`
        - `get_latest(k)` returns the version with highest semantic version number
        - `list_versions(k)` returns versions in ascending semver order
        - `unregister(k)` removes ALL versions of key `k`
        - `is_registered(k)` returns True if ANY version of `k` exists
        - `get(k)` returns same value as `get_latest(k)`

    Version Ordering:
        Implementations MUST use semantic versioning (MAJOR.MINOR.PATCH) by default.
        Alternative schemes (timestamps, integers) MAY be supported but MUST be
        documented clearly in implementation docstrings.
    """

    def register_version(self, key: K, version: str, value: V) -> None:
        """
        Register a specific version of a key-value pair.

        Adds or updates a versioned mapping. Multiple versions of the same key
        can coexist. Behavior for duplicate (key, version) pairs is implementation-
        specific (may overwrite or raise ValueError).

        Args:
            key: Registration key (must be hashable).
            version: Semantic version string (e.g., "1.2.3").
            value: Value to associate with this (key, version) pair.

        Raises:
            ValueError: If duplicate (key, version) and implementation forbids overwrites,
                       or if version string is invalid (e.g., not valid semver).
            RegistryError: If registration fails due to internal error.

        Thread Safety:
            Must be safe to call concurrently with other registry methods, including
            other `register_version()` calls for different versions of the same key.

        Example:
            >>> registry.register_version("api", "1.0.0", ApiV1Handler)
            >>> registry.register_version("api", "2.0.0", ApiV2Handler)
            >>> # Now two versions coexist
        """
        ...

    def get_version(self, key: K, version: str) -> V:
        """
        Retrieve a specific version of a registered value.

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
            >>> handler_v1 = registry.get_version("api", "1.0.0")
            >>> handler_v2 = registry.get_version("api", "2.0.0")
        """
        ...

    def get_latest(self, key: K) -> V:
        """
        Retrieve the latest version of a registered value.

        The "latest" version is determined by semantic versioning ordering
        (highest MAJOR.MINOR.PATCH wins). If multiple versions exist with
        same semver, behavior is implementation-specific.

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
            >>> registry.register_version("api", "1.0.0", ApiV1)
            >>> registry.register_version("api", "2.0.0", ApiV2)
            >>> latest = registry.get_latest("api")  # Returns ApiV2
        """
        ...

    def list_versions(self, key: K) -> list[str]:
        """
        List all registered versions for a key.

        Returns versions in ascending semantic version order (e.g., "1.0.0"
        before "2.0.0"). Returns empty list if key has no versions.

        Args:
            key: Key to list versions for.

        Returns:
            List of version strings in ascending semver order.
            Empty list if key not registered.

        Thread Safety:
            Must return a consistent snapshot. Concurrent version registrations
            during list construction must not cause corruption or exceptions.

        Example:
            >>> registry.register_version("api", "1.0.0", ApiV1)
            >>> registry.register_version("api", "2.0.0", ApiV2)
            >>> registry.register_version("api", "1.5.0", ApiV1_5)
            >>> versions = registry.list_versions("api")
            >>> # ["1.0.0", "1.5.0", "2.0.0"]
        """
        ...

    def get_all_versions(self, key: K) -> dict[str, V]:
        """
        Retrieve all versions of a registered key as a mapping.

        Returns a dictionary mapping version strings to their corresponding
        values. Useful for migration, rollback, or version comparison scenarios.

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
            >>> registry.register_version("policy", "1.0.0", PolicyV1)
            >>> registry.register_version("policy", "2.0.0", PolicyV2)
            >>> all_versions = registry.get_all_versions("policy")
            >>> # {"1.0.0": PolicyV1, "2.0.0": PolicyV2}
            >>>
            >>> # Migrate all policies
            >>> for version, policy_cls in all_versions.items():
            ...     migrate_policy(version, policy_cls)
        """
        ...
