"""Protocol for provider descriptor registry.

This module defines the protocol for managing provider descriptors at runtime.
Provider registries serve as the source of truth for available providers and
their capabilities, enabling dynamic discovery and routing.

Thread Safety:
    Implementations MUST be thread-safe for concurrent read/write operations.
    All mutation operations (register, unregister) must be atomic.

Usage:
    Use this protocol when:
    - You need to register and discover providers at runtime
    - You need capability-based provider discovery
    - You need tag-based filtering of providers

Example:
    >>> # Type checking only - actual implementation in omnibase_infra
    >>> from typing import TYPE_CHECKING
    >>> if TYPE_CHECKING:
    ...     from omnibase_core.models.providers import ModelProviderDescriptor
    >>>
    >>> class MyProviderRegistry:
    ...     def register(
    ...         self,
    ...         descriptor: "ModelProviderDescriptor",
    ...         *,
    ...         replace: bool = False,
    ...     ) -> None:
    ...         # Implementation here
    ...         ...

See Also:
    - ProtocolCapabilityRegistry: Registry for capability metadata
    - ProtocolRegistryBase: Generic registry base protocol
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.providers import ModelProviderDescriptor

__all__ = ["ProtocolProviderRegistry"]


@runtime_checkable
class ProtocolProviderRegistry(Protocol):
    """
    Registry protocol for provider descriptors.

    Provider registries maintain a collection of provider descriptors and
    enable discovery by provider ID, capability, or tags. This is the
    runtime source of truth for available providers.

    Thread Safety:
        Implementations MUST be thread-safe. Concurrent register/unregister/get
        operations must not corrupt internal state. Use locks or lock-free data
        structures as appropriate.

    Invariants:
        - After `register(d)`, `get(d.provider_id)` returns `d`
        - After `unregister(id)`, `get(id)` returns None
        - `list_all()` returns exactly the providers for which `get()` returns non-None
        - `find_by_capability(cap)` returns only providers with that capability
    """

    def register(
        self,
        descriptor: ModelProviderDescriptor,
        *,
        replace: bool = False,
    ) -> None:
        """
        Register a provider descriptor.

        Adds a provider to the registry. By default, registration fails if a
        provider with the same ID is already registered.

        Args:
            descriptor: The provider descriptor to register.
            replace: If True, replace existing provider with same ID.
                    If False (default), raise ValueError on duplicate.

        Returns:
            None.

        Raises:
            ValueError: If provider with same ID exists and replace=False.
            RegistryError: If registration fails due to internal error.

        Thread Safety:
            Must be safe to call concurrently with other registry methods.

        Example:
            >>> registry.register(provider_descriptor)
            >>> registry.register(updated_descriptor, replace=True)
        """
        ...

    def unregister(self, provider_id: str) -> None:
        """
        Remove a provider from the registry.

        Idempotent operation - safe to call with non-existent ID.

        Args:
            provider_id: ID of the provider to remove.

        Returns:
            None.

        Raises:
            RegistryError: If unregistration fails due to internal error.

        Thread Safety:
            Must be safe to call concurrently with other registry methods.

        Example:
            >>> registry.unregister("my-provider")
        """
        ...

    def get(self, provider_id: str) -> ModelProviderDescriptor | None:
        """
        Get a provider by ID.

        Args:
            provider_id: ID of the provider to retrieve.

        Returns:
            The provider descriptor if found, None otherwise.

        Raises:
            RegistryError: If retrieval fails due to internal error.

        Thread Safety:
            Result is a point-in-time snapshot. Provider may be registered
            or unregistered immediately after this call returns.

        Example:
            >>> provider = registry.get("my-provider")
            >>> if provider is not None:
            ...     print(f"Found: {provider.provider_id}")
        """
        ...

    def list_all(self) -> Sequence[ModelProviderDescriptor]:
        """
        List all registered providers.

        Returns a snapshot of currently registered providers. The returned
        sequence may become stale if concurrent modifications occur.

        Args:
            None.

        Returns:
            Sequence of all registered provider descriptors.
            Order is implementation-specific.

        Raises:
            RegistryError: If listing fails due to internal error.

        Thread Safety:
            Must return a consistent snapshot. Concurrent modifications
            during list construction must not cause corruption.

        Example:
            >>> for provider in registry.list_all():
            ...     print(provider.provider_id)
        """
        ...

    def get_available_capability_ids(self) -> Sequence[str]:
        """
        Get all capability IDs available across registered providers.

        Returns the union of all capability identifiers offered by all
        registered providers. This is useful for capability discovery.

        Note:
            This method returns capability IDs (strings), not full metadata.
            For capability metadata, use ProtocolCapabilityRegistry.

        Args:
            None.

        Returns:
            Sequence of unique capability identifiers.
            Order is implementation-specific.

        Raises:
            RegistryError: If listing fails due to internal error.

        Thread Safety:
            Result is a point-in-time snapshot.

        Example:
            >>> cap_ids = registry.get_available_capability_ids()
            >>> print(f"Available capabilities: {cap_ids}")
        """
        ...

    def find_by_capability(
        self,
        capability_id: str,
    ) -> Sequence[ModelProviderDescriptor]:
        """
        Find all providers that offer a specific capability.

        Args:
            capability_id: The capability identifier to search for.

        Returns:
            Sequence of providers offering the capability.
            Empty sequence if no providers match.

        Raises:
            RegistryError: If search fails due to internal error.

        Thread Safety:
            Result is a point-in-time snapshot.

        Example:
            >>> llm_providers = registry.find_by_capability("llm.completion")
            >>> for p in llm_providers:
            ...     print(f"Provider {p.provider_id} supports llm.completion")
        """
        ...

    def find_by_tags(
        self,
        tags: Sequence[str],
        *,
        match: Literal["any", "all"] = "any",
    ) -> Sequence[ModelProviderDescriptor]:
        """
        Find providers by tags.

        Args:
            tags: Tag values to search for.
            match: Matching mode.
                - "any": Return providers with at least one matching tag.
                - "all": Return only providers with all specified tags.

        Returns:
            Sequence of matching providers.
            Empty sequence if no providers match.

        Raises:
            RegistryError: If search fails due to internal error.

        Thread Safety:
            Result is a point-in-time snapshot.

        Example:
            >>> # Find providers with any of the tags
            >>> providers = registry.find_by_tags(["fast", "cheap"])
            >>>
            >>> # Find providers with ALL tags
            >>> providers = registry.find_by_tags(["fast", "cheap"], match="all")
        """
        ...
