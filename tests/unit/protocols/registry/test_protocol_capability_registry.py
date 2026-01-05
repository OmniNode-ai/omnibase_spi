"""
Tests for ProtocolCapabilityRegistry protocol.

Validates that ProtocolCapabilityRegistry:
- Is properly runtime checkable
- Defines required methods with correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
- Supports capability metadata registration and lookup operations
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

import pytest

from omnibase_spi.protocols.registry import ProtocolCapabilityRegistry

# =============================================================================
# Mock Models (since we can't import from omnibase_core in tests)
# =============================================================================


class MockCapabilityMetadata:
    """
    A mock that simulates ModelCapabilityMetadata from omnibase_core.

    Provides the minimal interface needed for testing ProtocolCapabilityRegistry.
    """

    def __init__(
        self,
        capability: str,
        name: str | None = None,
        description: str | None = None,
        version: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the mock capability metadata."""
        self._capability = capability
        self._name = name or capability
        self._description = description or ""
        self._version = version or "1.0.0"
        self._metadata = metadata if metadata is not None else {}

    @property
    def capability(self) -> str:
        """Return the capability identifier (semantic string)."""
        return self._capability

    @property
    def name(self) -> str:
        """Return the human-readable capability name."""
        return self._name

    @property
    def description(self) -> str:
        """Return the capability description."""
        return self._description

    @property
    def version(self) -> str:
        """Return the capability version."""
        return self._version

    @property
    def metadata(self) -> dict[str, Any]:
        """Return additional capability metadata."""
        return self._metadata


# =============================================================================
# Mock Implementations
# =============================================================================


class MockCapabilityRegistry:
    """
    A class that fully implements the ProtocolCapabilityRegistry protocol.

    This mock implementation provides an in-memory capability registry for testing.
    It demonstrates how a compliant implementation should behave.
    """

    def __init__(self) -> None:
        """Initialize the mock capability registry with empty storage."""
        self._capabilities: dict[str, MockCapabilityMetadata] = {}

    def register_capability(
        self,
        metadata: Any,  # Would be ModelCapabilityMetadata
        *,
        replace: bool = False,
    ) -> None:
        """
        Register capability metadata.

        Args:
            metadata: The capability metadata to register.
            replace: If True, replace existing metadata with same capability ID.

        Raises:
            ValueError: If capability already registered and replace=False.
        """
        if metadata.capability in self._capabilities and not replace:
            raise ValueError(
                f"Capability '{metadata.capability}' already registered. "
                "Use replace=True to update."
            )
        self._capabilities[metadata.capability] = metadata

    def get_capability(
        self,
        capability_id: str,
    ) -> Any | None:
        """
        Get capability metadata by ID.

        Args:
            capability_id: The capability identifier (semantic string).

        Returns:
            The capability metadata if found, None otherwise.
        """
        return self._capabilities.get(capability_id)

    def list_all(self) -> Sequence[Any]:
        """
        List all registered capability metadata.

        Returns:
            Sequence of all registered capability metadata.
        """
        return list(self._capabilities.values())


class PartialCapabilityRegistry:
    """A class that only implements some ProtocolCapabilityRegistry methods."""

    def register_capability(self, metadata: Any, *, replace: bool = False) -> None:
        """Only implement register_capability, missing other methods."""
        pass


class NonCompliantCapabilityRegistry:
    """A class that implements none of the ProtocolCapabilityRegistry methods."""

    pass


class MethodOnlyCapabilityRegistry:
    """A class that implements only get_capability and list_all."""

    def get_capability(self, capability_id: str) -> Any | None:
        """Return None."""
        return None

    def list_all(self) -> Sequence[Any]:
        """Return empty list."""
        return []


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestProtocolCapabilityRegistryProtocol:
    """Test suite for ProtocolCapabilityRegistry protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolCapabilityRegistry should be runtime_checkable."""
        # Check for either the old or new attribute name for runtime protocols
        assert hasattr(ProtocolCapabilityRegistry, "_is_runtime_protocol") or hasattr(
            ProtocolCapabilityRegistry, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolCapabilityRegistry should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolCapabilityRegistry.__mro__
        )

    def test_protocol_has_register_capability_method(self) -> None:
        """ProtocolCapabilityRegistry should define register_capability method."""
        assert "register_capability" in dir(ProtocolCapabilityRegistry)

    def test_protocol_has_get_capability_method(self) -> None:
        """ProtocolCapabilityRegistry should define get_capability method."""
        assert "get_capability" in dir(ProtocolCapabilityRegistry)

    def test_protocol_has_list_all_method(self) -> None:
        """ProtocolCapabilityRegistry should define list_all method."""
        assert "list_all" in dir(ProtocolCapabilityRegistry)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolCapabilityRegistry protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolCapabilityRegistry()  # type: ignore[misc]


@pytest.mark.unit
class TestProtocolCapabilityRegistryCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all methods should pass isinstance check."""
        registry = MockCapabilityRegistry()
        assert isinstance(registry, ProtocolCapabilityRegistry)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        registry = PartialCapabilityRegistry()
        assert not isinstance(registry, ProtocolCapabilityRegistry)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no methods should fail isinstance check."""
        registry = NonCompliantCapabilityRegistry()
        assert not isinstance(registry, ProtocolCapabilityRegistry)

    def test_method_only_fails_isinstance(self) -> None:
        """A class missing register_capability should fail isinstance check."""
        registry = MethodOnlyCapabilityRegistry()
        assert not isinstance(registry, ProtocolCapabilityRegistry)


@pytest.mark.unit
class TestMockCapabilityRegistryImplementsAllMethods:
    """Test that MockCapabilityRegistry has all required members."""

    def test_mock_has_register_capability_method(self) -> None:
        """Mock should have register_capability method."""
        registry = MockCapabilityRegistry()
        assert hasattr(registry, "register_capability")
        assert callable(registry.register_capability)

    def test_mock_has_get_capability_method(self) -> None:
        """Mock should have get_capability method."""
        registry = MockCapabilityRegistry()
        assert hasattr(registry, "get_capability")
        assert callable(registry.get_capability)

    def test_mock_has_list_all_method(self) -> None:
        """Mock should have list_all method."""
        registry = MockCapabilityRegistry()
        assert hasattr(registry, "list_all")
        assert callable(registry.list_all)


@pytest.mark.unit
class TestCapabilityRegistration:
    """Test capability registration functionality."""

    def test_register_capability(self) -> None:
        """Should successfully register a capability."""
        registry = MockCapabilityRegistry()
        metadata = MockCapabilityMetadata(capability="llm.completion")

        registry.register_capability(metadata)

        assert registry.get_capability("llm.completion") is metadata

    def test_register_duplicate_raises_error(self) -> None:
        """Should raise ValueError when registering duplicate without replace."""
        registry = MockCapabilityRegistry()
        metadata1 = MockCapabilityMetadata(capability="llm.completion")
        metadata2 = MockCapabilityMetadata(capability="llm.completion")

        registry.register_capability(metadata1)

        with pytest.raises(ValueError) as exc_info:
            registry.register_capability(metadata2)

        assert "llm.completion" in str(exc_info.value)
        assert "already registered" in str(exc_info.value)

    def test_register_with_replace_updates_capability(self) -> None:
        """Should update capability when using replace=True."""
        registry = MockCapabilityRegistry()
        metadata1 = MockCapabilityMetadata(capability="llm.completion", version="1.0.0")
        metadata2 = MockCapabilityMetadata(capability="llm.completion", version="2.0.0")

        registry.register_capability(metadata1)
        registry.register_capability(metadata2, replace=True)

        result = registry.get_capability("llm.completion")
        assert result is metadata2
        assert result.version == "2.0.0"

    def test_register_multiple_capabilities(self) -> None:
        """Should successfully register multiple different capabilities."""
        registry = MockCapabilityRegistry()
        meta1 = MockCapabilityMetadata(capability="llm.completion")
        meta2 = MockCapabilityMetadata(capability="llm.embedding")
        meta3 = MockCapabilityMetadata(capability="llm.chat")

        registry.register_capability(meta1)
        registry.register_capability(meta2)
        registry.register_capability(meta3)

        assert len(registry.list_all()) == 3
        assert registry.get_capability("llm.completion") is meta1
        assert registry.get_capability("llm.embedding") is meta2
        assert registry.get_capability("llm.chat") is meta3


@pytest.mark.unit
class TestCapabilityLookup:
    """Test capability lookup functionality."""

    def test_get_capability_existing(self) -> None:
        """Should return capability when it exists."""
        registry = MockCapabilityRegistry()
        metadata = MockCapabilityMetadata(
            capability="llm.completion",
            name="LLM Completion",
            version="1.0.0",
        )

        registry.register_capability(metadata)

        result = registry.get_capability("llm.completion")
        assert result is metadata
        assert result.name == "LLM Completion"
        assert result.version == "1.0.0"

    def test_get_capability_nonexistent_returns_none(self) -> None:
        """Should return None for non-existent capability."""
        registry = MockCapabilityRegistry()

        result = registry.get_capability("nonexistent-capability")
        assert result is None

    def test_list_all_empty_registry(self) -> None:
        """Should return empty sequence for empty registry."""
        registry = MockCapabilityRegistry()

        result = registry.list_all()
        assert len(result) == 0

    def test_list_all_returns_all_capabilities(self) -> None:
        """Should return all registered capabilities."""
        registry = MockCapabilityRegistry()
        meta1 = MockCapabilityMetadata(capability="cap-a")
        meta2 = MockCapabilityMetadata(capability="cap-b")

        registry.register_capability(meta1)
        registry.register_capability(meta2)

        result = registry.list_all()
        assert len(result) == 2
        capability_ids = {c.capability for c in result}
        assert capability_ids == {"cap-a", "cap-b"}


@pytest.mark.unit
class TestRegistryInvariants:
    """Test registry invariants documented in the protocol."""

    def test_invariant_register_then_get(self) -> None:
        """After register_capability(m), get_capability(m.capability) returns m."""
        registry = MockCapabilityRegistry()
        metadata = MockCapabilityMetadata(capability="test-cap")

        registry.register_capability(metadata)
        result = registry.get_capability("test-cap")

        assert result is metadata

    def test_invariant_list_all_consistent_with_get(self) -> None:
        """list_all() returns exactly the capabilities for which get_capability() returns non-None."""
        registry = MockCapabilityRegistry()
        meta1 = MockCapabilityMetadata(capability="cap-a")
        meta2 = MockCapabilityMetadata(capability="cap-b")
        meta3 = MockCapabilityMetadata(capability="cap-c")

        registry.register_capability(meta1)
        registry.register_capability(meta2)
        registry.register_capability(meta3)

        listed = registry.list_all()
        listed_ids = {c.capability for c in listed}

        # Check all listed items can be retrieved
        for cap in listed:
            assert registry.get_capability(cap.capability) is not None

        # Check consistency
        assert len(listed_ids) == 3
        for cap_id in ["cap-a", "cap-b", "cap-c"]:
            result = registry.get_capability(cap_id)
            if result is not None:
                assert cap_id in listed_ids

    def test_invariant_list_all_no_duplicates(self) -> None:
        """list_all() should not contain duplicates."""
        registry = MockCapabilityRegistry()
        meta1 = MockCapabilityMetadata(capability="cap-a")
        meta2 = MockCapabilityMetadata(capability="cap-b")

        registry.register_capability(meta1)
        registry.register_capability(meta2)
        # Re-register with replace
        registry.register_capability(
            MockCapabilityMetadata(capability="cap-a", version="2.0"),
            replace=True,
        )

        listed = registry.list_all()
        capability_ids = [c.capability for c in listed]

        # Check no duplicates
        assert len(capability_ids) == len(set(capability_ids))


@pytest.mark.unit
class TestProtocolCapabilityRegistryImports:
    """Test protocol imports from different locations."""

    def test_import_from_registry_module(self) -> None:
        """Test direct import from protocol_capability_registry module."""
        from omnibase_spi.protocols.registry.protocol_capability_registry import (
            ProtocolCapabilityRegistry as DirectProtocolCapabilityRegistry,
        )

        registry = MockCapabilityRegistry()
        assert isinstance(registry, DirectProtocolCapabilityRegistry)

    def test_import_from_registry_package(self) -> None:
        """Test import from registry package."""
        from omnibase_spi.protocols.registry import (
            ProtocolCapabilityRegistry as RegistryProtocolCapabilityRegistry,
        )

        registry = MockCapabilityRegistry()
        assert isinstance(registry, RegistryProtocolCapabilityRegistry)

    def test_import_from_protocols_package(self) -> None:
        """Test import from protocols root package."""
        from omnibase_spi.protocols import (
            ProtocolCapabilityRegistry as ProtocolsCapabilityRegistry,
        )

        registry = MockCapabilityRegistry()
        assert isinstance(registry, ProtocolsCapabilityRegistry)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols import (
            ProtocolCapabilityRegistry as ProtocolsCapabilityRegistry,
        )
        from omnibase_spi.protocols.registry import (
            ProtocolCapabilityRegistry as RegistryProtocolCapabilityRegistry,
        )
        from omnibase_spi.protocols.registry.protocol_capability_registry import (
            ProtocolCapabilityRegistry as DirectProtocolCapabilityRegistry,
        )

        assert DirectProtocolCapabilityRegistry is RegistryProtocolCapabilityRegistry
        assert RegistryProtocolCapabilityRegistry is ProtocolsCapabilityRegistry


@pytest.mark.unit
class TestProtocolCapabilityRegistryDocumentation:
    """Test that ProtocolCapabilityRegistry has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolCapabilityRegistry should have a docstring."""
        assert ProtocolCapabilityRegistry.__doc__ is not None
        assert len(ProtocolCapabilityRegistry.__doc__.strip()) > 0

    def test_docstring_mentions_thread_safety(self) -> None:
        """Docstring should mention thread safety requirements."""
        doc = ProtocolCapabilityRegistry.__doc__ or ""
        assert "thread" in doc.lower() or "Thread" in doc

    def test_docstring_mentions_optional_nature(self) -> None:
        """Docstring should mention this registry is optional."""
        doc = ProtocolCapabilityRegistry.__doc__ or ""
        assert "optional" in doc.lower()

    def test_docstring_mentions_invariants(self) -> None:
        """Docstring should document invariants."""
        doc = ProtocolCapabilityRegistry.__doc__ or ""
        assert "Invariant" in doc or "invariant" in doc


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases for ProtocolCapabilityRegistry."""

    def test_empty_capability_id(self) -> None:
        """Should handle empty capability ID correctly."""
        registry = MockCapabilityRegistry()
        metadata = MockCapabilityMetadata(capability="")

        registry.register_capability(metadata)
        assert registry.get_capability("") is metadata

    def test_semantic_capability_ids(self) -> None:
        """Should handle semantic capability IDs (e.g., 'llm.completion')."""
        registry = MockCapabilityRegistry()
        meta1 = MockCapabilityMetadata(capability="llm.completion")
        meta2 = MockCapabilityMetadata(capability="llm.embedding.text")
        meta3 = MockCapabilityMetadata(capability="storage.vector.upsert")

        registry.register_capability(meta1)
        registry.register_capability(meta2)
        registry.register_capability(meta3)

        assert registry.get_capability("llm.completion") is meta1
        assert registry.get_capability("llm.embedding.text") is meta2
        assert registry.get_capability("storage.vector.upsert") is meta3

    def test_capability_with_all_fields(self) -> None:
        """Should handle capability with all metadata fields."""
        registry = MockCapabilityRegistry()
        metadata = MockCapabilityMetadata(
            capability="llm.completion",
            name="LLM Text Completion",
            description="Generates text completions using large language models",
            version="2.1.0",
            metadata={
                "max_tokens": 4096,
                "models": ["gpt-4", "claude-3"],
                "streaming": True,
            },
        )

        registry.register_capability(metadata)
        result = registry.get_capability("llm.completion")

        assert result is not None
        assert result.capability == "llm.completion"
        assert result.name == "LLM Text Completion"
        assert "large language models" in result.description
        assert result.version == "2.1.0"
        assert result.metadata["max_tokens"] == 4096
        assert result.metadata["streaming"] is True

    def test_case_sensitive_capability_ids(self) -> None:
        """Capability IDs should be case-sensitive."""
        registry = MockCapabilityRegistry()
        meta1 = MockCapabilityMetadata(capability="LLM.Completion")
        meta2 = MockCapabilityMetadata(capability="llm.completion")

        registry.register_capability(meta1)
        registry.register_capability(meta2)

        assert registry.get_capability("LLM.Completion") is meta1
        assert registry.get_capability("llm.completion") is meta2
        assert len(registry.list_all()) == 2


@pytest.mark.unit
class TestUsagePatterns:
    """Test common usage patterns for ProtocolCapabilityRegistry."""

    def test_capability_discovery_pattern(self) -> None:
        """Test typical capability discovery workflow."""
        registry = MockCapabilityRegistry()

        # Register capabilities
        registry.register_capability(
            MockCapabilityMetadata(
                capability="llm.completion",
                name="LLM Completion",
                description="Text completion capability",
            )
        )
        registry.register_capability(
            MockCapabilityMetadata(
                capability="llm.embedding",
                name="LLM Embedding",
                description="Text embedding capability",
            )
        )

        # Discovery pattern: list all and filter
        all_caps = registry.list_all()
        llm_caps = [c for c in all_caps if c.capability.startswith("llm.")]

        assert len(llm_caps) == 2
        assert all(c.capability.startswith("llm.") for c in llm_caps)

    def test_documentation_generation_pattern(self) -> None:
        """Test capability documentation generation pattern."""
        registry = MockCapabilityRegistry()

        registry.register_capability(
            MockCapabilityMetadata(
                capability="llm.completion",
                name="LLM Completion",
                description="Generates text completions",
                version="1.0.0",
            )
        )
        registry.register_capability(
            MockCapabilityMetadata(
                capability="llm.chat",
                name="LLM Chat",
                description="Multi-turn conversation",
                version="2.0.0",
            )
        )

        # Documentation generation pattern
        docs = []
        for cap in registry.list_all():
            docs.append(
                f"## {cap.name} (v{cap.version})\n"
                f"ID: `{cap.capability}`\n"
                f"{cap.description}\n"
            )

        assert len(docs) == 2
        assert any("LLM Completion" in doc for doc in docs)
        assert any("llm.chat" in doc for doc in docs)

    def test_version_update_pattern(self) -> None:
        """Test capability version update workflow."""
        registry = MockCapabilityRegistry()

        # Register initial version
        v1 = MockCapabilityMetadata(
            capability="llm.completion",
            version="1.0.0",
        )
        registry.register_capability(v1)

        # Check current version
        current = registry.get_capability("llm.completion")
        assert current is not None
        assert current.version == "1.0.0"

        # Update to new version
        v2 = MockCapabilityMetadata(
            capability="llm.completion",
            version="2.0.0",
        )
        registry.register_capability(v2, replace=True)

        # Verify update
        updated = registry.get_capability("llm.completion")
        assert updated is not None
        assert updated.version == "2.0.0"
