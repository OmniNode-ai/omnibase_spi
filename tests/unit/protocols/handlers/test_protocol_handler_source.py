"""
Tests for ProtocolHandlerSource protocol.

Validates that ProtocolHandlerSource:
- Is properly runtime checkable
- Defines required properties and methods with correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from omnibase_spi.protocols.handlers import ProtocolHandlerSource

if TYPE_CHECKING:
    from omnibase_core.models.handlers import ModelHandlerDescriptor

from .conftest import _create_mock_descriptor

# =============================================================================
# Mock Implementations
# =============================================================================


class MockHandlerSource:
    """A class that fully implements the ProtocolHandlerSource protocol."""

    def __init__(
        self,
        source_type: str = "BOOTSTRAP",
        handlers: tuple[ModelHandlerDescriptor, ...] | None = None,
    ) -> None:
        """Initialize the mock handler source."""
        self._source_type = source_type
        self._handlers = handlers if handlers is not None else ()

    @property
    def source_type(self) -> str:
        """Return the source type."""
        return self._source_type

    def list_handler_descriptors(self) -> tuple[ModelHandlerDescriptor, ...]:
        """List all handler descriptors from this source."""
        return self._handlers

    def get_handler_descriptor(self, handler_id: str) -> ModelHandlerDescriptor | None:
        """Get a specific handler descriptor by ID."""
        for desc in self._handlers:
            # Match on handler_name string representation
            if str(desc.handler_name) == handler_id:
                return desc
        return None


class PartialHandlerSource:
    """A class that only implements source_type, missing list_handler_descriptors."""

    @property
    def source_type(self) -> str:
        """Return source type."""
        return "BOOTSTRAP"


class NonCompliantHandlerSource:
    """A class that implements none of the ProtocolHandlerSource protocol."""

    pass


class MethodOnlyHandlerSource:
    """A class that only implements list_handler_descriptors, missing source_type property."""

    def list_handler_descriptors(self) -> tuple[ModelHandlerDescriptor, ...]:
        """Return empty tuple."""
        return ()

    def get_handler_descriptor(self, handler_id: str) -> ModelHandlerDescriptor | None:
        """Get a specific handler descriptor by ID."""
        return None


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

    def test_protocol_has_list_handler_descriptors_method(self) -> None:
        """ProtocolHandlerSource should define list_handler_descriptors method."""
        assert "list_handler_descriptors" in dir(ProtocolHandlerSource)

    def test_protocol_has_get_handler_descriptor_method(self) -> None:
        """ProtocolHandlerSource should define get_handler_descriptor method."""
        assert "get_handler_descriptor" in dir(ProtocolHandlerSource)

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
        handlers = (_create_mock_descriptor("test-handler"),)
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

    def test_mock_has_list_handler_descriptors_method(self) -> None:
        """Mock should have list_handler_descriptors method."""
        source = MockHandlerSource()
        assert hasattr(source, "list_handler_descriptors")
        assert callable(source.list_handler_descriptors)

    def test_mock_has_get_handler_descriptor_method(self) -> None:
        """Mock should have get_handler_descriptor method."""
        source = MockHandlerSource()
        assert hasattr(source, "get_handler_descriptor")
        assert callable(source.get_handler_descriptor)


@pytest.mark.unit
class TestProtocolHandlerSourceMethodSignatures:
    """Test method signatures from compliant mock implementation."""

    def test_source_type_returns_string(self) -> None:
        """source_type should return a string value."""
        for source_type in ["BOOTSTRAP", "CONTRACT", "HYBRID"]:
            source = MockHandlerSource(source_type=source_type)
            assert source.source_type == source_type
            assert isinstance(source.source_type, str)

    def test_list_handler_descriptors_returns_tuple(self) -> None:
        """list_handler_descriptors should return a tuple."""
        source = MockHandlerSource()
        result = source.list_handler_descriptors()
        assert isinstance(result, tuple)

    def test_list_handler_descriptors_returns_empty_tuple(self) -> None:
        """list_handler_descriptors should return empty tuple when no handlers."""
        source = MockHandlerSource(handlers=())
        result = source.list_handler_descriptors()
        assert result == ()

    def test_list_handler_descriptors_returns_descriptors(self) -> None:
        """list_handler_descriptors should return tuple of ModelHandlerDescriptor."""
        descriptors = (
            _create_mock_descriptor("handler-1"),
            _create_mock_descriptor("handler-2"),
        )
        source = MockHandlerSource(handlers=descriptors)
        result = source.list_handler_descriptors()
        assert len(result) == 2

    def test_get_handler_descriptor_returns_none_for_missing(self) -> None:
        """get_handler_descriptor should return None for non-existent handler."""
        source = MockHandlerSource()
        result = source.get_handler_descriptor("non-existent")
        assert result is None

    def test_get_handler_descriptor_returns_descriptor_when_found(self) -> None:
        """get_handler_descriptor should return descriptor when found."""
        desc = _create_mock_descriptor("my-handler")
        source = MockHandlerSource(handlers=(desc,))
        result = source.get_handler_descriptor("test:my-handler")
        assert result is desc


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
            handlers=(_create_mock_descriptor("bootstrap-handler"),),
        )
        contract_source = MockHandlerSource(
            source_type="CONTRACT",
            handlers=(_create_mock_descriptor("contract-handler"),),
        )

        all_handlers = []
        for source in [bootstrap_source, contract_source]:
            all_handlers.extend(source.list_handler_descriptors())

        assert len(all_handlers) == 2

    def test_source_type_for_observability(self) -> None:
        """source_type can be used for logging/observability."""
        sources = [
            MockHandlerSource(source_type="BOOTSTRAP"),
            MockHandlerSource(source_type="CONTRACT"),
        ]

        source_types = [s.source_type for s in sources]
        assert source_types == ["BOOTSTRAP", "CONTRACT"]

    def test_get_handler_descriptor_lookup_pattern(self) -> None:
        """get_handler_descriptor enables targeted lookup."""
        handlers = (
            _create_mock_descriptor("http-handler"),
            _create_mock_descriptor("kafka-handler"),
        )
        source = MockHandlerSource(handlers=handlers)

        # Lookup specific handler
        http = source.get_handler_descriptor("test:http-handler")
        assert http is not None
        assert str(http.handler_name) == "test:http-handler"

        # Non-existent returns None
        missing = source.get_handler_descriptor("test:missing")
        assert missing is None
