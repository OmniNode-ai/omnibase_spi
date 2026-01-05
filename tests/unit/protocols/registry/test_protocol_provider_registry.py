"""
Tests for ProtocolProviderRegistry protocol.

Validates that ProtocolProviderRegistry:
- Is properly runtime checkable
- Defines required methods with correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
- Supports provider registration, lookup, and filtering operations
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal, Protocol

import pytest

from omnibase_spi.protocols.registry import ProtocolProviderRegistry

# =============================================================================
# Mock Models (since we can't import from omnibase_core in tests)
# =============================================================================


class MockProviderDescriptor:
    """
    A mock that simulates ModelProviderDescriptor from omnibase_core.

    Provides the minimal interface needed for testing ProtocolProviderRegistry.
    """

    def __init__(
        self,
        provider_id: str,
        capabilities: list[str] | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the mock provider descriptor."""
        self._provider_id = provider_id
        self._capabilities = capabilities if capabilities is not None else []
        self._tags = tags if tags is not None else []
        self._metadata = metadata if metadata is not None else {}

    @property
    def provider_id(self) -> str:
        """Return the provider ID."""
        return self._provider_id

    @property
    def capabilities(self) -> list[str]:
        """Return list of capability IDs this provider offers."""
        return self._capabilities

    @property
    def tags(self) -> list[str]:
        """Return tags associated with this provider."""
        return self._tags

    @property
    def metadata(self) -> dict[str, Any]:
        """Return provider metadata."""
        return self._metadata


# =============================================================================
# Mock Implementations
# =============================================================================


class MockProviderRegistry:
    """
    A class that fully implements the ProtocolProviderRegistry protocol.

    This mock implementation provides an in-memory provider registry for testing.
    It demonstrates how a compliant implementation should behave.
    """

    def __init__(self) -> None:
        """Initialize the mock provider registry with empty storage."""
        self._providers: dict[str, MockProviderDescriptor] = {}

    def register(
        self,
        descriptor: Any,  # Would be ModelProviderDescriptor
        *,
        replace: bool = False,
    ) -> None:
        """
        Register a provider descriptor.

        Args:
            descriptor: The provider descriptor to register.
            replace: If True, replace existing provider with same ID.

        Raises:
            ValueError: If provider with same ID exists and replace=False.
        """
        if descriptor.provider_id in self._providers and not replace:
            raise ValueError(
                f"Provider '{descriptor.provider_id}' already registered. "
                "Use replace=True to update."
            )
        self._providers[descriptor.provider_id] = descriptor

    def unregister(self, provider_id: str) -> None:
        """
        Remove a provider from the registry.

        Idempotent operation - safe to call with non-existent ID.

        Args:
            provider_id: ID of the provider to remove.
        """
        self._providers.pop(provider_id, None)

    def get(self, provider_id: str) -> Any | None:
        """
        Get a provider by ID.

        Args:
            provider_id: ID of the provider to retrieve.

        Returns:
            The provider descriptor if found, None otherwise.
        """
        return self._providers.get(provider_id)

    def list_all(self) -> Sequence[Any]:
        """
        List all registered providers.

        Returns:
            Sequence of all registered provider descriptors.
        """
        return list(self._providers.values())

    async def get_available_capability_ids(self) -> Sequence[str]:
        """
        Get all capability IDs available across registered providers.

        Returns:
            Sequence of unique capability identifiers.
        """
        capability_ids: set[str] = set()
        for provider in self._providers.values():
            capability_ids.update(provider.capabilities)
        return list(capability_ids)

    def find_by_capability(
        self,
        capability_id: str,
    ) -> Sequence[Any]:
        """
        Find all providers that offer a specific capability.

        Args:
            capability_id: The capability identifier to search for.

        Returns:
            Sequence of providers offering the capability.
        """
        return [p for p in self._providers.values() if capability_id in p.capabilities]

    def find_by_tags(
        self,
        tags: Sequence[str],
        *,
        match: Literal["any", "all"] = "any",
    ) -> Sequence[Any]:
        """
        Find providers by tags.

        Args:
            tags: Tag values to search for.
            match: Matching mode - "any" or "all".

        Returns:
            Sequence of matching providers.
        """
        tags_set = set(tags)
        if match == "any":
            return [
                p for p in self._providers.values() if tags_set.intersection(p.tags)
            ]
        else:  # match == "all"
            return [
                p for p in self._providers.values() if tags_set.issubset(set(p.tags))
            ]


class PartialProviderRegistry:
    """A class that only implements some ProtocolProviderRegistry methods."""

    def register(self, descriptor: Any, *, replace: bool = False) -> None:
        """Only implement register, missing other methods."""
        pass

    def get(self, provider_id: str) -> Any | None:
        """Only implement get."""
        return None


class NonCompliantProviderRegistry:
    """A class that implements none of the ProtocolProviderRegistry methods."""

    pass


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestProtocolProviderRegistryProtocol:
    """Test suite for ProtocolProviderRegistry protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolProviderRegistry should be runtime_checkable."""
        # Check for either the old or new attribute name for runtime protocols
        assert hasattr(ProtocolProviderRegistry, "_is_runtime_protocol") or hasattr(
            ProtocolProviderRegistry, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolProviderRegistry should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolProviderRegistry.__mro__
        )

    def test_protocol_has_register_method(self) -> None:
        """ProtocolProviderRegistry should define register method."""
        assert "register" in dir(ProtocolProviderRegistry)

    def test_protocol_has_unregister_method(self) -> None:
        """ProtocolProviderRegistry should define unregister method."""
        assert "unregister" in dir(ProtocolProviderRegistry)

    def test_protocol_has_get_method(self) -> None:
        """ProtocolProviderRegistry should define get method."""
        assert "get" in dir(ProtocolProviderRegistry)

    def test_protocol_has_list_all_method(self) -> None:
        """ProtocolProviderRegistry should define list_all method."""
        assert "list_all" in dir(ProtocolProviderRegistry)

    def test_protocol_has_get_available_capability_ids_method(self) -> None:
        """ProtocolProviderRegistry should define get_available_capability_ids method."""
        assert "get_available_capability_ids" in dir(ProtocolProviderRegistry)

    def test_protocol_has_find_by_capability_method(self) -> None:
        """ProtocolProviderRegistry should define find_by_capability method."""
        assert "find_by_capability" in dir(ProtocolProviderRegistry)

    def test_protocol_has_find_by_tags_method(self) -> None:
        """ProtocolProviderRegistry should define find_by_tags method."""
        assert "find_by_tags" in dir(ProtocolProviderRegistry)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolProviderRegistry protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolProviderRegistry()  # type: ignore[misc]


@pytest.mark.unit
class TestProtocolProviderRegistryCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all methods should pass isinstance check."""
        registry = MockProviderRegistry()
        assert isinstance(registry, ProtocolProviderRegistry)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        registry = PartialProviderRegistry()
        assert not isinstance(registry, ProtocolProviderRegistry)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no methods should fail isinstance check."""
        registry = NonCompliantProviderRegistry()
        assert not isinstance(registry, ProtocolProviderRegistry)


@pytest.mark.unit
class TestMockProviderRegistryImplementsAllMethods:
    """Test that MockProviderRegistry has all required members."""

    def test_mock_has_register_method(self) -> None:
        """Mock should have register method."""
        registry = MockProviderRegistry()
        assert hasattr(registry, "register")
        assert callable(registry.register)

    def test_mock_has_unregister_method(self) -> None:
        """Mock should have unregister method."""
        registry = MockProviderRegistry()
        assert hasattr(registry, "unregister")
        assert callable(registry.unregister)

    def test_mock_has_get_method(self) -> None:
        """Mock should have get method."""
        registry = MockProviderRegistry()
        assert hasattr(registry, "get")
        assert callable(registry.get)

    def test_mock_has_list_all_method(self) -> None:
        """Mock should have list_all method."""
        registry = MockProviderRegistry()
        assert hasattr(registry, "list_all")
        assert callable(registry.list_all)

    def test_mock_has_get_available_capability_ids_method(self) -> None:
        """Mock should have get_available_capability_ids method."""
        registry = MockProviderRegistry()
        assert hasattr(registry, "get_available_capability_ids")
        assert callable(registry.get_available_capability_ids)

    def test_mock_has_find_by_capability_method(self) -> None:
        """Mock should have find_by_capability method."""
        registry = MockProviderRegistry()
        assert hasattr(registry, "find_by_capability")
        assert callable(registry.find_by_capability)

    def test_mock_has_find_by_tags_method(self) -> None:
        """Mock should have find_by_tags method."""
        registry = MockProviderRegistry()
        assert hasattr(registry, "find_by_tags")
        assert callable(registry.find_by_tags)


@pytest.mark.unit
class TestProviderRegistration:
    """Test provider registration functionality."""

    def test_register_provider(self) -> None:
        """Should successfully register a provider."""
        registry = MockProviderRegistry()
        descriptor = MockProviderDescriptor(provider_id="test-provider")

        registry.register(descriptor)

        assert registry.get("test-provider") is descriptor

    def test_register_duplicate_raises_error(self) -> None:
        """Should raise ValueError when registering duplicate without replace."""
        registry = MockProviderRegistry()
        descriptor1 = MockProviderDescriptor(provider_id="test-provider")
        descriptor2 = MockProviderDescriptor(provider_id="test-provider")

        registry.register(descriptor1)

        with pytest.raises(ValueError) as exc_info:
            registry.register(descriptor2)

        assert "test-provider" in str(exc_info.value)
        assert "already registered" in str(exc_info.value)

    def test_register_with_replace_updates_provider(self) -> None:
        """Should update provider when using replace=True."""
        registry = MockProviderRegistry()
        descriptor1 = MockProviderDescriptor(
            provider_id="test-provider", metadata={"version": "1.0"}
        )
        descriptor2 = MockProviderDescriptor(
            provider_id="test-provider", metadata={"version": "2.0"}
        )

        registry.register(descriptor1)
        registry.register(descriptor2, replace=True)

        result = registry.get("test-provider")
        assert result is descriptor2
        assert result.metadata["version"] == "2.0"

    def test_register_multiple_providers(self) -> None:
        """Should successfully register multiple different providers."""
        registry = MockProviderRegistry()
        desc1 = MockProviderDescriptor(provider_id="provider-1")
        desc2 = MockProviderDescriptor(provider_id="provider-2")
        desc3 = MockProviderDescriptor(provider_id="provider-3")

        registry.register(desc1)
        registry.register(desc2)
        registry.register(desc3)

        assert len(registry.list_all()) == 3
        assert registry.get("provider-1") is desc1
        assert registry.get("provider-2") is desc2
        assert registry.get("provider-3") is desc3


@pytest.mark.unit
class TestProviderUnregistration:
    """Test provider unregistration functionality."""

    def test_unregister_existing_provider(self) -> None:
        """Should successfully unregister an existing provider."""
        registry = MockProviderRegistry()
        descriptor = MockProviderDescriptor(provider_id="test-provider")

        registry.register(descriptor)
        assert registry.get("test-provider") is not None

        registry.unregister("test-provider")
        assert registry.get("test-provider") is None

    def test_unregister_nonexistent_is_idempotent(self) -> None:
        """Should not raise error when unregistering non-existent provider."""
        registry = MockProviderRegistry()

        # Should not raise
        registry.unregister("nonexistent-provider")

    def test_unregister_twice_is_idempotent(self) -> None:
        """Should not raise error when unregistering same provider twice."""
        registry = MockProviderRegistry()
        descriptor = MockProviderDescriptor(provider_id="test-provider")

        registry.register(descriptor)
        registry.unregister("test-provider")
        # Second unregister should not raise
        registry.unregister("test-provider")


@pytest.mark.unit
class TestProviderLookup:
    """Test provider lookup functionality."""

    def test_get_existing_provider(self) -> None:
        """Should return provider when it exists."""
        registry = MockProviderRegistry()
        descriptor = MockProviderDescriptor(provider_id="test-provider")

        registry.register(descriptor)

        result = registry.get("test-provider")
        assert result is descriptor

    def test_get_nonexistent_returns_none(self) -> None:
        """Should return None for non-existent provider."""
        registry = MockProviderRegistry()

        result = registry.get("nonexistent-provider")
        assert result is None

    def test_list_all_empty_registry(self) -> None:
        """Should return empty sequence for empty registry."""
        registry = MockProviderRegistry()

        result = registry.list_all()
        assert len(result) == 0

    def test_list_all_returns_all_providers(self) -> None:
        """Should return all registered providers."""
        registry = MockProviderRegistry()
        desc1 = MockProviderDescriptor(provider_id="provider-1")
        desc2 = MockProviderDescriptor(provider_id="provider-2")

        registry.register(desc1)
        registry.register(desc2)

        result = registry.list_all()
        assert len(result) == 2
        provider_ids = {p.provider_id for p in result}
        assert provider_ids == {"provider-1", "provider-2"}


@pytest.mark.unit
class TestCapabilityDiscovery:
    """Test capability discovery functionality."""

    @pytest.mark.asyncio
    async def test_get_available_capability_ids_empty(self) -> None:
        """Should return empty sequence when no providers registered."""
        registry = MockProviderRegistry()

        result = await registry.get_available_capability_ids()
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_available_capability_ids_returns_all_capabilities(self) -> None:
        """Should return all unique capabilities from all providers."""
        registry = MockProviderRegistry()
        desc1 = MockProviderDescriptor(
            provider_id="provider-1", capabilities=["cap-a", "cap-b"]
        )
        desc2 = MockProviderDescriptor(
            provider_id="provider-2", capabilities=["cap-b", "cap-c"]
        )

        registry.register(desc1)
        registry.register(desc2)

        result = await registry.get_available_capability_ids()
        assert set(result) == {"cap-a", "cap-b", "cap-c"}

    def test_find_by_capability_returns_matching_providers(self) -> None:
        """Should return providers that offer the specified capability."""
        registry = MockProviderRegistry()
        desc1 = MockProviderDescriptor(
            provider_id="provider-1", capabilities=["llm.completion", "llm.chat"]
        )
        desc2 = MockProviderDescriptor(
            provider_id="provider-2", capabilities=["llm.embedding"]
        )
        desc3 = MockProviderDescriptor(
            provider_id="provider-3", capabilities=["llm.completion"]
        )

        registry.register(desc1)
        registry.register(desc2)
        registry.register(desc3)

        result = registry.find_by_capability("llm.completion")
        provider_ids = {p.provider_id for p in result}
        assert provider_ids == {"provider-1", "provider-3"}

    def test_find_by_capability_returns_empty_for_unknown(self) -> None:
        """Should return empty sequence for unknown capability."""
        registry = MockProviderRegistry()
        desc = MockProviderDescriptor(provider_id="provider-1", capabilities=["cap-a"])

        registry.register(desc)

        result = registry.find_by_capability("unknown-capability")
        assert len(result) == 0


@pytest.mark.unit
class TestTagFiltering:
    """Test tag-based filtering functionality."""

    def test_find_by_tags_match_any(self) -> None:
        """Should return providers with at least one matching tag."""
        registry = MockProviderRegistry()
        desc1 = MockProviderDescriptor(provider_id="provider-1", tags=["fast", "cheap"])
        desc2 = MockProviderDescriptor(
            provider_id="provider-2", tags=["slow", "expensive"]
        )
        desc3 = MockProviderDescriptor(
            provider_id="provider-3", tags=["fast", "expensive"]
        )

        registry.register(desc1)
        registry.register(desc2)
        registry.register(desc3)

        result = registry.find_by_tags(["fast", "cheap"], match="any")
        provider_ids = {p.provider_id for p in result}
        assert provider_ids == {"provider-1", "provider-3"}

    def test_find_by_tags_match_all(self) -> None:
        """Should return only providers with all specified tags."""
        registry = MockProviderRegistry()
        desc1 = MockProviderDescriptor(
            provider_id="provider-1", tags=["fast", "cheap", "reliable"]
        )
        desc2 = MockProviderDescriptor(provider_id="provider-2", tags=["fast"])
        desc3 = MockProviderDescriptor(provider_id="provider-3", tags=["fast", "cheap"])

        registry.register(desc1)
        registry.register(desc2)
        registry.register(desc3)

        result = registry.find_by_tags(["fast", "cheap"], match="all")
        provider_ids = {p.provider_id for p in result}
        assert provider_ids == {"provider-1", "provider-3"}

    def test_find_by_tags_returns_empty_for_no_match(self) -> None:
        """Should return empty sequence when no providers match."""
        registry = MockProviderRegistry()
        desc = MockProviderDescriptor(provider_id="provider-1", tags=["fast"])

        registry.register(desc)

        result = registry.find_by_tags(["nonexistent-tag"])
        assert len(result) == 0

    def test_find_by_tags_default_match_is_any(self) -> None:
        """Default match mode should be 'any'."""
        registry = MockProviderRegistry()
        desc1 = MockProviderDescriptor(provider_id="provider-1", tags=["tag-a"])
        desc2 = MockProviderDescriptor(provider_id="provider-2", tags=["tag-b"])

        registry.register(desc1)
        registry.register(desc2)

        # Without specifying match, should default to "any"
        result = registry.find_by_tags(["tag-a", "tag-b"])
        assert len(result) == 2


@pytest.mark.unit
class TestRegistryInvariants:
    """Test registry invariants documented in the protocol."""

    def test_invariant_register_then_get(self) -> None:
        """After register(d), get(d.provider_id) returns d."""
        registry = MockProviderRegistry()
        descriptor = MockProviderDescriptor(provider_id="test-id")

        registry.register(descriptor)
        result = registry.get("test-id")

        assert result is descriptor

    def test_invariant_unregister_then_get_none(self) -> None:
        """After unregister(id), get(id) returns None."""
        registry = MockProviderRegistry()
        descriptor = MockProviderDescriptor(provider_id="test-id")

        registry.register(descriptor)
        registry.unregister("test-id")
        result = registry.get("test-id")

        assert result is None

    def test_invariant_list_all_consistent_with_get(self) -> None:
        """list_all() returns exactly the providers for which get() returns non-None."""
        registry = MockProviderRegistry()
        desc1 = MockProviderDescriptor(provider_id="p1")
        desc2 = MockProviderDescriptor(provider_id="p2")
        desc3 = MockProviderDescriptor(provider_id="p3")

        registry.register(desc1)
        registry.register(desc2)
        registry.register(desc3)
        registry.unregister("p2")

        listed = registry.list_all()
        listed_ids = {p.provider_id for p in listed}

        # Check consistency with get()
        for provider_id in ["p1", "p2", "p3"]:
            if registry.get(provider_id) is not None:
                assert provider_id in listed_ids
            else:
                assert provider_id not in listed_ids

    def test_invariant_find_by_capability_only_matching(self) -> None:
        """find_by_capability(cap) returns only providers with that capability."""
        registry = MockProviderRegistry()
        desc1 = MockProviderDescriptor(provider_id="p1", capabilities=["cap-x"])
        desc2 = MockProviderDescriptor(provider_id="p2", capabilities=["cap-y"])

        registry.register(desc1)
        registry.register(desc2)

        result = registry.find_by_capability("cap-x")
        for provider in result:
            assert "cap-x" in provider.capabilities


@pytest.mark.unit
class TestProtocolProviderRegistryImports:
    """Test protocol imports from different locations."""

    def test_import_from_registry_module(self) -> None:
        """Test direct import from protocol_provider_registry module."""
        from omnibase_spi.protocols.registry.protocol_provider_registry import (
            ProtocolProviderRegistry as DirectProtocolProviderRegistry,
        )

        registry = MockProviderRegistry()
        assert isinstance(registry, DirectProtocolProviderRegistry)

    def test_import_from_registry_package(self) -> None:
        """Test import from registry package."""
        from omnibase_spi.protocols.registry import (
            ProtocolProviderRegistry as RegistryProtocolProviderRegistry,
        )

        registry = MockProviderRegistry()
        assert isinstance(registry, RegistryProtocolProviderRegistry)

    def test_import_from_protocols_package(self) -> None:
        """Test import from protocols root package."""
        from omnibase_spi.protocols import (
            ProtocolProviderRegistry as ProtocolsProviderRegistry,
        )

        registry = MockProviderRegistry()
        assert isinstance(registry, ProtocolsProviderRegistry)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols import (
            ProtocolProviderRegistry as ProtocolsProviderRegistry,
        )
        from omnibase_spi.protocols.registry import (
            ProtocolProviderRegistry as RegistryProtocolProviderRegistry,
        )
        from omnibase_spi.protocols.registry.protocol_provider_registry import (
            ProtocolProviderRegistry as DirectProtocolProviderRegistry,
        )

        assert DirectProtocolProviderRegistry is RegistryProtocolProviderRegistry
        assert RegistryProtocolProviderRegistry is ProtocolsProviderRegistry


@pytest.mark.unit
class TestProtocolProviderRegistryDocumentation:
    """Test that ProtocolProviderRegistry has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolProviderRegistry should have a docstring."""
        assert ProtocolProviderRegistry.__doc__ is not None
        assert len(ProtocolProviderRegistry.__doc__.strip()) > 0

    def test_docstring_mentions_thread_safety(self) -> None:
        """Docstring should mention thread safety requirements."""
        doc = ProtocolProviderRegistry.__doc__ or ""
        assert "thread" in doc.lower() or "Thread" in doc

    def test_docstring_mentions_invariants(self) -> None:
        """Docstring should document invariants."""
        doc = ProtocolProviderRegistry.__doc__ or ""
        assert "Invariant" in doc or "invariant" in doc


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases for ProtocolProviderRegistry."""

    def test_empty_provider_id(self) -> None:
        """Should handle empty provider ID correctly."""
        registry = MockProviderRegistry()
        descriptor = MockProviderDescriptor(provider_id="")

        registry.register(descriptor)
        assert registry.get("") is descriptor

    def test_provider_with_no_capabilities(self) -> None:
        """Should handle provider with no capabilities."""
        registry = MockProviderRegistry()
        descriptor = MockProviderDescriptor(provider_id="empty-caps")

        registry.register(descriptor)
        result = registry.find_by_capability("any-cap")
        assert len(result) == 0

    def test_provider_with_no_tags(self) -> None:
        """Should handle provider with no tags."""
        registry = MockProviderRegistry()
        descriptor = MockProviderDescriptor(provider_id="no-tags")

        registry.register(descriptor)
        result = registry.find_by_tags(["any-tag"])
        assert len(result) == 0

    def test_find_by_empty_tags_list(self) -> None:
        """Should handle empty tags list correctly."""
        registry = MockProviderRegistry()
        descriptor = MockProviderDescriptor(provider_id="test", tags=["tag-a"])

        registry.register(descriptor)
        result = registry.find_by_tags([], match="any")
        # Empty tags means no match with "any"
        assert len(result) == 0

    def test_find_by_empty_tags_match_all(self) -> None:
        """Should handle empty tags list with match='all'."""
        registry = MockProviderRegistry()
        descriptor = MockProviderDescriptor(provider_id="test", tags=["tag-a"])

        registry.register(descriptor)
        result = registry.find_by_tags([], match="all")
        # Empty set is subset of any set, so all providers match
        assert len(result) == 1
