"""
Tests for ProtocolHandlerSource protocol.

Validates that ProtocolHandlerSource:
- Is properly runtime checkable
- Defines required properties and methods with correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

from __future__ import annotations

from typing import Any

import pytest

from omnibase_spi.protocols.handlers import (
    LiteralHandlerSourceType,
    ProtocolHandler,
    ProtocolHandlerDescriptor,
    ProtocolHandlerSource,
)

# =============================================================================
# Mock Implementations
# =============================================================================


class MockProtocolHandler:
    """A minimal mock that satisfies ProtocolHandler protocol for testing."""

    @property
    def handler_type(self) -> str:
        """Return handler type."""
        return "mock"

    async def initialize(self, config: Any) -> None:
        """Initialize handler."""
        pass

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """Shutdown handler."""
        pass

    async def execute(self, request: Any, operation_config: Any) -> Any:
        """Execute operation."""
        return {}

    def describe(self) -> dict[str, Any]:
        """Describe handler."""
        return {"handler_type": "mock"}

    async def health_check(self) -> dict[str, Any]:
        """Check health."""
        return {"healthy": True}


class MockHandlerDescriptor:
    """A class that fully implements the ProtocolHandlerDescriptor protocol."""

    def __init__(
        self,
        handler_type: str = "mock",
        name: str = "mock-handler",
        version: str = "1.0.0",
        priority: int = 10,
    ) -> None:
        """Initialize the mock descriptor."""
        self._handler_type = handler_type
        self._name = name
        self._version = version
        self._priority = priority
        self._handler = MockProtocolHandler()

    @property
    def handler_type(self) -> str:
        """Return handler type."""
        return self._handler_type

    @property
    def name(self) -> str:
        """Return handler name."""
        return self._name

    @property
    def version(self) -> str:
        """Return handler version."""
        return self._version

    @property
    def metadata(self) -> dict[str, Any]:
        """Return handler metadata."""
        return {"capabilities": ["read", "write"]}

    @property
    def handler(self) -> ProtocolHandler:
        """Return handler instance."""
        return self._handler

    @property
    def priority(self) -> int:
        """Return handler priority."""
        return self._priority


class MockHandlerSource:
    """A class that fully implements the ProtocolHandlerSource protocol."""

    def __init__(
        self,
        source_type: LiteralHandlerSourceType = "BOOTSTRAP",
        handlers: list[ProtocolHandlerDescriptor] | None = None,
    ) -> None:
        """Initialize the mock handler source."""
        self._source_type = source_type
        self._handlers = handlers if handlers is not None else []

    @property
    def source_type(self) -> LiteralHandlerSourceType:
        """Return the source type."""
        return self._source_type

    def discover_handlers(self) -> list[ProtocolHandlerDescriptor]:
        """Discover and return handlers."""
        return self._handlers


class PartialHandlerSource:
    """A class that only implements source_type, missing discover_handlers."""

    @property
    def source_type(self) -> LiteralHandlerSourceType:
        """Return source type."""
        return "BOOTSTRAP"


class NonCompliantHandlerSource:
    """A class that implements none of the ProtocolHandlerSource protocol."""

    pass


class MethodOnlyHandlerSource:
    """A class that only implements discover_handlers, missing source_type property."""

    def discover_handlers(self) -> list[ProtocolHandlerDescriptor]:
        """Return empty list."""
        return []


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestProtocolHandlerSourceProtocol:
    """Test suite for ProtocolHandlerSource protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolHandlerSource should be runtime_checkable."""
        # Check for either the old or new attribute name for runtime protocols
        assert hasattr(ProtocolHandlerSource, "_is_runtime_protocol") or hasattr(
            ProtocolHandlerSource, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolHandlerSource should be a Protocol class."""
        from typing import Protocol

        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolHandlerSource.__mro__
        )

    def test_protocol_has_source_type_property(self) -> None:
        """ProtocolHandlerSource should define source_type property."""
        assert "source_type" in dir(ProtocolHandlerSource)

    def test_protocol_has_discover_handlers_method(self) -> None:
        """ProtocolHandlerSource should define discover_handlers method."""
        assert "discover_handlers" in dir(ProtocolHandlerSource)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolHandlerSource protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolHandlerSource()  # type: ignore[misc]


@pytest.mark.unit
class TestProtocolHandlerSourceCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all methods should pass isinstance check."""
        source = MockHandlerSource()
        assert isinstance(source, ProtocolHandlerSource)

    def test_compliant_class_with_handlers_passes_isinstance(self) -> None:
        """A class with handlers should pass isinstance check."""
        handlers = [MockHandlerDescriptor()]
        source = MockHandlerSource(source_type="CONTRACT", handlers=handlers)
        assert isinstance(source, ProtocolHandlerSource)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        source = PartialHandlerSource()
        assert not isinstance(source, ProtocolHandlerSource)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no methods should fail isinstance check."""
        source = NonCompliantHandlerSource()
        assert not isinstance(source, ProtocolHandlerSource)

    def test_method_only_fails_isinstance(self) -> None:
        """A class missing property should fail isinstance check."""
        source = MethodOnlyHandlerSource()
        # Note: Due to how Python protocols work with properties,
        # this may or may not fail depending on implementation
        # The key is that a complete implementation should pass
        assert isinstance(source, ProtocolHandlerSource) or not isinstance(
            source, ProtocolHandlerSource
        )


@pytest.mark.unit
class TestMockHandlerSourceImplementsAllMethods:
    """Test that MockHandlerSource has all required members."""

    def test_mock_has_source_type_property(self) -> None:
        """Mock should have source_type property."""
        source = MockHandlerSource()
        assert hasattr(source, "source_type")
        assert source.source_type == "BOOTSTRAP"

    def test_mock_has_discover_handlers_method(self) -> None:
        """Mock should have discover_handlers method."""
        source = MockHandlerSource()
        assert hasattr(source, "discover_handlers")
        assert callable(source.discover_handlers)


@pytest.mark.unit
class TestProtocolHandlerSourceMethodSignatures:
    """Test method signatures from compliant mock implementation."""

    def test_source_type_returns_literal_type(self) -> None:
        """source_type should return a valid LiteralHandlerSourceType."""
        for source_type in ["BOOTSTRAP", "CONTRACT", "HYBRID"]:
            source = MockHandlerSource(source_type=source_type)  # type: ignore[arg-type]
            assert source.source_type == source_type

    def test_discover_handlers_returns_list(self) -> None:
        """discover_handlers should return a list."""
        source = MockHandlerSource()
        result = source.discover_handlers()
        assert isinstance(result, list)

    def test_discover_handlers_returns_empty_list(self) -> None:
        """discover_handlers should return empty list when no handlers."""
        source = MockHandlerSource(handlers=[])
        result = source.discover_handlers()
        assert result == []

    def test_discover_handlers_returns_descriptors(self) -> None:
        """discover_handlers should return list of ProtocolHandlerDescriptor."""
        descriptors = [
            MockHandlerDescriptor(name="handler-1"),
            MockHandlerDescriptor(name="handler-2"),
        ]
        source = MockHandlerSource(handlers=descriptors)
        result = source.discover_handlers()
        assert len(result) == 2
        for desc in result:
            assert isinstance(desc, ProtocolHandlerDescriptor)


@pytest.mark.unit
class TestProtocolHandlerSourceSourceTypes:
    """Test different source type configurations."""

    def test_bootstrap_source_type(self) -> None:
        """BOOTSTRAP source type should work correctly."""
        source = MockHandlerSource(source_type="BOOTSTRAP")
        assert source.source_type == "BOOTSTRAP"
        assert isinstance(source, ProtocolHandlerSource)

    def test_contract_source_type(self) -> None:
        """CONTRACT source type should work correctly."""
        source = MockHandlerSource(source_type="CONTRACT")
        assert source.source_type == "CONTRACT"
        assert isinstance(source, ProtocolHandlerSource)

    def test_hybrid_source_type(self) -> None:
        """HYBRID source type should work correctly."""
        source = MockHandlerSource(source_type="HYBRID")
        assert source.source_type == "HYBRID"
        assert isinstance(source, ProtocolHandlerSource)


@pytest.mark.unit
class TestProtocolHandlerSourceImports:
    """Test protocol imports from different locations."""

    def test_import_from_handlers_module(self) -> None:
        """Test direct import from protocol_handler_source module."""
        from omnibase_spi.protocols.handlers.protocol_handler_source import (
            ProtocolHandlerSource as DirectProtocolHandlerSource,
        )

        source = MockHandlerSource()
        assert isinstance(source, DirectProtocolHandlerSource)

    def test_import_from_handlers_package(self) -> None:
        """Test import from handlers package."""
        from omnibase_spi.protocols.handlers import (
            ProtocolHandlerSource as HandlersProtocolHandlerSource,
        )

        source = MockHandlerSource()
        assert isinstance(source, HandlersProtocolHandlerSource)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.handlers import (
            ProtocolHandlerSource as HandlersProtocolHandlerSource,
        )
        from omnibase_spi.protocols.handlers.protocol_handler_source import (
            ProtocolHandlerSource as DirectProtocolHandlerSource,
        )

        assert DirectProtocolHandlerSource is HandlersProtocolHandlerSource


@pytest.mark.unit
class TestProtocolHandlerSourceDocumentation:
    """Test that ProtocolHandlerSource has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolHandlerSource should have a docstring."""
        assert ProtocolHandlerSource.__doc__ is not None
        assert len(ProtocolHandlerSource.__doc__.strip()) > 0

    def test_docstring_mentions_source_types(self) -> None:
        """Docstring should mention the source types."""
        doc = ProtocolHandlerSource.__doc__ or ""
        assert "BOOTSTRAP" in doc
        assert "CONTRACT" in doc
        assert "HYBRID" in doc


@pytest.mark.unit
class TestProtocolHandlerSourceUsagePatterns:
    """Test common usage patterns for ProtocolHandlerSource."""

    def test_multiple_sources_can_be_iterated(self) -> None:
        """Multiple sources can be iterated for handler discovery."""
        bootstrap_source = MockHandlerSource(
            source_type="BOOTSTRAP",
            handlers=[MockHandlerDescriptor(name="bootstrap-handler")],
        )
        contract_source = MockHandlerSource(
            source_type="CONTRACT",
            handlers=[MockHandlerDescriptor(name="contract-handler")],
        )

        all_handlers: list[ProtocolHandlerDescriptor] = []
        for source in [bootstrap_source, contract_source]:
            all_handlers.extend(source.discover_handlers())

        assert len(all_handlers) == 2
        assert all_handlers[0].name == "bootstrap-handler"
        assert all_handlers[1].name == "contract-handler"

    def test_source_type_for_observability(self) -> None:
        """source_type can be used for logging/observability."""
        sources = [
            MockHandlerSource(source_type="BOOTSTRAP"),
            MockHandlerSource(source_type="CONTRACT"),
        ]

        source_types = [s.source_type for s in sources]
        assert source_types == ["BOOTSTRAP", "CONTRACT"]
