"""Generic registry protocol for key-value registration management.

This module provides a generic, type-safe protocol for implementing registries
that map keys to values. It serves as the foundational interface that specialized
registries (like ProtocolHandlerRegistry) can extend or implement.

Thread Safety:
    Implementations MUST be thread-safe for concurrent read/write operations.
    Callers should not assume thread safety - always check implementation docs.

Type Parameters:
    K: Key type (e.g., str, enum, type). Must be hashable.
    V: Value type (e.g., handler class, service instance, configuration).

Usage:
    Use this protocol when:
    - Building a new registry implementation with custom key/value types
    - You need generic registry behavior without domain-specific methods
    - Type safety for registry operations is critical

    Use specialized protocols when:
    - Domain-specific validation is required (e.g., ProtocolHandlerRegistry)
    - Additional methods beyond basic CRUD are needed
    - Integration with existing domain models is required

Example:
    >>> # Define a registry for mapping service names to service classes
    >>> from typing import runtime_checkable, Protocol
    >>>
    >>> @runtime_checkable
    >>> class ProtocolServiceRegistry(ProtocolRegistryBase[str, type]):
    ...     '''Registry for service implementations.'''
    ...     pass
    >>>
    >>> # Implement the registry
    >>> class ServiceRegistry:
    ...     def __init__(self):
    ...         self._registry: dict[str, type] = {}
    ...
    ...     def register(self, key: str, value: type) -> None:
    ...         self._registry[key] = value
    ...
    ...     def get(self, key: str) -> type:
    ...         if key not in self._registry:
    ...             raise KeyError(f"Service not registered: {key}")
    ...         return self._registry[key]
    ...
    ...     def list_keys(self) -> list[str]:
    ...         return list(self._registry.keys())
    ...
    ...     def is_registered(self, key: str) -> bool:
    ...         return key in self._registry
    ...
    ...     def unregister(self, key: str) -> bool:
    ...         if key in self._registry:
    ...             del self._registry[key]
    ...             return True
    ...         return False

See Also:
    - ProtocolHandlerRegistry: Specialized registry for protocol handlers
    - ProtocolServiceRegistry: Specialized registry for service instances
"""

from __future__ import annotations

from typing import Generic, Protocol, TypeVar, runtime_checkable

__all__ = ["ProtocolRegistryBase"]

# Type variables for generic registry
K = TypeVar("K")  # Key type (must be hashable in implementations)
V = TypeVar("V")  # Value type


@runtime_checkable
class ProtocolRegistryBase(Protocol, Generic[K, V]):
    """
    Generic protocol for key-value registry implementations.

    This protocol defines the core interface for registries that map keys to values.
    It provides type-safe CRUD operations and serves as the foundation for specialized
    registry protocols in the ONEX framework.

    Type Parameters:
        K: Key type (must be hashable in concrete implementations)
        V: Value type (can be any type)

    Thread Safety:
        Implementations MUST be thread-safe. Concurrent register/unregister/get
        operations must not corrupt internal state. Use locks or lock-free data
        structures as appropriate.

    Error Handling:
        - `get()` MUST raise KeyError if key not found
        - `register()` MAY raise ValueError for duplicate keys (implementation-specific)
        - `unregister()` MUST NOT raise for non-existent keys (returns False instead)

    Invariants:
        - After `register(k, v)`, `is_registered(k)` returns True
        - After `unregister(k)`, `is_registered(k)` returns False
        - `get(k)` only succeeds if `is_registered(k)` is True
        - `list_keys()` contains exactly the keys for which `is_registered()` is True
    """

    def register(self, key: K, value: V) -> None:
        """
        Register a key-value pair in the registry.

        Adds or updates a key-value mapping. Behavior for duplicate keys is
        implementation-specific (may overwrite or raise ValueError).

        Args:
            key: Registration key (must be hashable).
            value: Value to associate with the key.

        Raises:
            ValueError: If duplicate key and implementation forbids overwrites.
            RegistryError: If registration fails due to internal error.

        Thread Safety:
            Must be safe to call concurrently with other registry methods.

        Example:
            >>> registry.register("service_a", ServiceAImpl)
            >>> registry.register("service_b", ServiceBImpl)
        """
        ...

    def get(self, key: K) -> V:
        """
        Retrieve the value associated with a key.

        Args:
            key: Registration key to lookup.

        Returns:
            Value associated with the key.

        Raises:
            KeyError: If key is not registered.
            RegistryError: If retrieval fails due to internal error.

        Thread Safety:
            Must be safe to call concurrently with register/unregister.

        Example:
            >>> service_cls = registry.get("service_a")
            >>> service = service_cls()
        """
        ...

    def list_keys(self) -> list[K]:
        """
        List all registered keys.

        Returns a snapshot of currently registered keys. The returned list
        may become stale if concurrent modifications occur.

        Returns:
            List of all registered keys. Empty list if no keys registered.
            Order is implementation-specific (may be insertion order, sorted, etc.).

        Thread Safety:
            Must return a consistent snapshot. Concurrent modifications during
            list construction must not cause corruption or exceptions.

        Example:
            >>> keys = registry.list_keys()
            >>> for key in keys:
            ...     print(f"{key} -> {registry.get(key)}")
        """
        ...

    def is_registered(self, key: K) -> bool:
        """
        Check if a key is registered.

        Args:
            key: Key to check.

        Returns:
            True if key is registered, False otherwise.

        Thread Safety:
            Result is a point-in-time snapshot. Key may be registered/unregistered
            immediately after this call returns.

        Example:
            >>> if registry.is_registered("service_a"):
            ...     service = registry.get("service_a")
            ... else:
            ...     print("Service not available")
        """
        ...

    def unregister(self, key: K) -> bool:
        """
        Remove a key-value pair from the registry.

        Idempotent operation - safe to call multiple times with same key.

        Args:
            key: Key to remove.

        Returns:
            True if key was registered and removed.
            False if key was not registered (no-op).

        Thread Safety:
            Must be safe to call concurrently with other registry methods.
            If multiple threads unregister same key, only one returns True.

        Example:
            >>> if registry.unregister("service_a"):
            ...     print("Service unregistered")
            ... else:
            ...     print("Service was not registered")
        """
        ...
