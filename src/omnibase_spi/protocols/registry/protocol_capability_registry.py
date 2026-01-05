"""Protocol for capability metadata registry.

This module defines the protocol for managing capability metadata at runtime.
Capability registries are optional and used for discovery and documentation
of available capabilities in the system.

Thread Safety:
    Implementations MUST be thread-safe for concurrent read/write operations.
    All mutation operations (register_capability) must be atomic.

Usage:
    Use this protocol when:
    - You need to document available capabilities
    - You need capability discovery/introspection
    - You need to validate capability requirements

Example:
    >>> # Type checking only - actual implementation in omnibase_infra
    >>> from typing import TYPE_CHECKING
    >>> if TYPE_CHECKING:
    ...     from omnibase_core.models.capabilities import ModelCapabilityMetadata
    >>>
    >>> class MyCapabilityRegistry:
    ...     def register_capability(
    ...         self,
    ...         metadata: "ModelCapabilityMetadata",
    ...         *,
    ...         replace: bool = False,
    ...     ) -> None:
    ...         # Implementation here
    ...         ...

See Also:
    - ProtocolProviderRegistry: Registry for provider descriptors
    - ModelCapabilityMetadata: Core model for capability metadata
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.capabilities import ModelCapabilityMetadata

__all__ = ["ProtocolCapabilityRegistry"]


@runtime_checkable
class ProtocolCapabilityRegistry(Protocol):
    """
    Registry protocol for capability metadata (optional feature).

    Capability registries maintain metadata about available capabilities,
    enabling discovery and documentation. Unlike ProtocolProviderRegistry
    (which is required for resolution), this registry is optional and
    primarily used for introspection.

    Thread Safety:
        Implementations MUST be thread-safe. Concurrent register/get
        operations must not corrupt internal state.

    Invariants:
        - After `register_capability(m)`, `get_capability(m.capability)` returns `m`
        - `list_all()` returns exactly the capabilities for which
          `get_capability()` returns non-None

    Note:
        Capability identifiers are semantic strings (e.g., "llm.completion"),
        not UUIDs. This makes them human-readable and predictable.
    """

    def register_capability(
        self,
        metadata: ModelCapabilityMetadata,
        *,
        replace: bool = False,
    ) -> None:
        """
        Register capability metadata.

        Adds capability metadata to the registry. By default, registration
        fails if metadata for the same capability is already registered.

        Args:
            metadata: The capability metadata to register.
            replace: If True, replace existing metadata with same capability ID.
                    If False (default), raise ValueError on duplicate.

        Raises:
            ValueError: If capability already registered and replace=False.
            RegistryError: If registration fails due to internal error.

        Thread Safety:
            Must be safe to call concurrently with other registry methods.

        Example:
            >>> registry.register_capability(capability_metadata)
            >>> registry.register_capability(updated_metadata, replace=True)
        """
        ...

    async def get_capability(
        self,
        capability_id: str,
    ) -> ModelCapabilityMetadata | None:
        """
        Get capability metadata by ID.

        Args:
            capability_id: The capability identifier (semantic string).

        Returns:
            The capability metadata if found, None otherwise.

        Thread Safety:
            Result is a point-in-time snapshot.

        Example:
            >>> cap = await registry.get_capability("llm.completion")
            >>> if cap is not None:
            ...     print(f"Name: {cap.name}, Version: {cap.version}")
        """
        ...

    async def list_all(self) -> Sequence[ModelCapabilityMetadata]:
        """
        List all registered capability metadata.

        Returns a snapshot of all registered capability metadata. Useful
        for documentation generation or capability introspection.

        Note:
            This method follows the same pattern as
            ProtocolProviderRegistry.list_all() - returning all entries
            in the registry.

        Returns:
            Sequence of all registered capability metadata.
            Order is implementation-specific.

        Thread Safety:
            Must return a consistent snapshot. Concurrent modifications
            during list construction must not cause corruption.

        Example:
            >>> for cap in await registry.list_all():
            ...     print(f"{cap.capability}: {cap.description}")
        """
        ...
