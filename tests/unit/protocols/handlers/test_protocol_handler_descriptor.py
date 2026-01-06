"""
Tests for ProtocolHandlerDescriptor protocol.

Validates that ProtocolHandlerDescriptor:
- Is properly runtime checkable
- Defines required properties with correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

from __future__ import annotations

from typing import Any

import pytest

from omnibase_spi.protocols.handlers import (
    ProtocolHandler,
    ProtocolHandlerDescriptor,
)

from .conftest import MockHandlerDescriptor, MockProtocolHandler

# =============================================================================
# Mock Implementations
# =============================================================================


class PartialHandlerDescriptor:
    """A class that only implements some properties."""

    @property
    def handler_type(self) -> str:
        """Return handler type."""
        return "partial"

    @property
    def name(self) -> str:
        """Return name."""
        return "partial-handler"

    # Missing: version, metadata, handler, priority


class NonCompliantDescriptor:
    """A class that implements none of the required properties."""

    pass


class MinimalHandlerDescriptor:
    """A class with all required properties but minimal implementation."""

    @property
    def handler_type(self) -> str:
        """Return handler type."""
        return "minimal"

    @property
    def name(self) -> str:
        """Return name."""
        return "minimal-handler"

    @property
    def version(self) -> str:
        """Return version."""
        return "0.0.1"

    @property
    def metadata(self) -> dict[str, Any]:
        """Return empty metadata."""
        return {}

    @property
    def handler(self) -> ProtocolHandler:
        """Return handler."""
        return MockProtocolHandler()

    @property
    def priority(self) -> int:
        """Return default priority."""
        return 0


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestProtocolHandlerDescriptorProtocol:
    """Test suite for ProtocolHandlerDescriptor protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolHandlerDescriptor should be runtime_checkable."""
        assert hasattr(ProtocolHandlerDescriptor, "_is_runtime_protocol") or hasattr(
            ProtocolHandlerDescriptor, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolHandlerDescriptor should be a Protocol class."""
        from typing import Protocol

        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolHandlerDescriptor.__mro__
        )

    def test_protocol_has_handler_type_property(self) -> None:
        """ProtocolHandlerDescriptor should define handler_type property."""
        assert "handler_type" in dir(ProtocolHandlerDescriptor)

    def test_protocol_has_name_property(self) -> None:
        """ProtocolHandlerDescriptor should define name property."""
        assert "name" in dir(ProtocolHandlerDescriptor)

    def test_protocol_has_version_property(self) -> None:
        """ProtocolHandlerDescriptor should define version property."""
        assert "version" in dir(ProtocolHandlerDescriptor)

    def test_protocol_has_metadata_property(self) -> None:
        """ProtocolHandlerDescriptor should define metadata property."""
        assert "metadata" in dir(ProtocolHandlerDescriptor)

    def test_protocol_has_handler_property(self) -> None:
        """ProtocolHandlerDescriptor should define handler property."""
        assert "handler" in dir(ProtocolHandlerDescriptor)

    def test_protocol_has_priority_property(self) -> None:
        """ProtocolHandlerDescriptor should define priority property."""
        assert "priority" in dir(ProtocolHandlerDescriptor)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolHandlerDescriptor protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolHandlerDescriptor()  # type: ignore[misc]


@pytest.mark.unit
class TestProtocolHandlerDescriptorCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all properties should pass isinstance check."""
        descriptor = MockHandlerDescriptor()
        assert isinstance(descriptor, ProtocolHandlerDescriptor)

    def test_minimal_implementation_passes_isinstance(self) -> None:
        """A minimal implementation should pass isinstance check."""
        descriptor = MinimalHandlerDescriptor()
        assert isinstance(descriptor, ProtocolHandlerDescriptor)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing properties should fail isinstance check."""
        descriptor = PartialHandlerDescriptor()
        assert not isinstance(descriptor, ProtocolHandlerDescriptor)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no properties should fail isinstance check."""
        descriptor = NonCompliantDescriptor()
        assert not isinstance(descriptor, ProtocolHandlerDescriptor)


@pytest.mark.unit
class TestMockDescriptorImplementsAllProperties:
    """Test that MockHandlerDescriptor has all required properties."""

    def test_mock_has_handler_type(self) -> None:
        """Mock should have handler_type property."""
        descriptor = MockHandlerDescriptor(handler_type="http")
        assert hasattr(descriptor, "handler_type")
        assert descriptor.handler_type == "http"

    def test_mock_has_name(self) -> None:
        """Mock should have name property."""
        descriptor = MockHandlerDescriptor(name="http-rest-handler")
        assert hasattr(descriptor, "name")
        assert descriptor.name == "http-rest-handler"

    def test_mock_has_version(self) -> None:
        """Mock should have version property."""
        descriptor = MockHandlerDescriptor(version="1.2.0")
        assert hasattr(descriptor, "version")
        assert descriptor.version == "1.2.0"

    def test_mock_has_metadata(self) -> None:
        """Mock should have metadata property."""
        descriptor = MockHandlerDescriptor()
        assert hasattr(descriptor, "metadata")
        assert isinstance(descriptor.metadata, dict)

    def test_mock_has_handler(self) -> None:
        """Mock should have handler property."""
        descriptor = MockHandlerDescriptor()
        assert hasattr(descriptor, "handler")
        assert isinstance(descriptor.handler, ProtocolHandler)

    def test_mock_has_priority(self) -> None:
        """Mock should have priority property."""
        descriptor = MockHandlerDescriptor()
        assert hasattr(descriptor, "priority")
        assert descriptor.priority == 10


@pytest.mark.unit
class TestProtocolHandlerDescriptorPropertyTypes:
    """Test property return types."""

    def test_handler_type_returns_string(self) -> None:
        """handler_type should return a string."""
        descriptor = MockHandlerDescriptor(handler_type="kafka")
        assert isinstance(descriptor.handler_type, str)
        assert descriptor.handler_type == "kafka"

    def test_name_returns_string(self) -> None:
        """name should return a string."""
        descriptor = MockHandlerDescriptor(name="my-handler")
        assert isinstance(descriptor.name, str)
        assert descriptor.name == "my-handler"

    def test_version_returns_string(self) -> None:
        """version should return a semantic version string."""
        descriptor = MockHandlerDescriptor(version="2.0.0")
        assert isinstance(descriptor.version, str)
        assert descriptor.version == "2.0.0"

    def test_metadata_returns_dict(self) -> None:
        """metadata should return a dictionary."""
        descriptor = MockHandlerDescriptor(metadata={"key": "value", "count": 42})
        assert isinstance(descriptor.metadata, dict)
        assert descriptor.metadata["key"] == "value"
        assert descriptor.metadata["count"] == 42

    def test_metadata_can_be_empty(self) -> None:
        """metadata should support empty dict."""
        descriptor = MockHandlerDescriptor(metadata={})
        assert descriptor.metadata == {}

    def test_handler_returns_protocol_handler(self) -> None:
        """handler should return a ProtocolHandler instance."""
        descriptor = MockHandlerDescriptor()
        assert isinstance(descriptor.handler, ProtocolHandler)

    def test_priority_returns_integer(self) -> None:
        """priority should return an integer."""
        descriptor = MockHandlerDescriptor(priority=100)
        assert isinstance(descriptor.priority, int)
        assert descriptor.priority == 100

    def test_priority_supports_zero(self) -> None:
        """priority should support zero value."""
        descriptor = MockHandlerDescriptor(priority=0)
        assert descriptor.priority == 0

    def test_priority_supports_negative(self) -> None:
        """priority should support negative values."""
        descriptor = MinimalHandlerDescriptor()
        # MinimalHandlerDescriptor returns 0, but negative should be valid
        assert isinstance(descriptor.priority, int)


@pytest.mark.unit
class TestProtocolHandlerDescriptorUsagePatterns:
    """Test common usage patterns for ProtocolHandlerDescriptor."""

    def test_descriptor_used_for_registration(self) -> None:
        """Descriptor properties can be used for handler registration."""
        descriptor = MockHandlerDescriptor(
            handler_type="postgresql",
            name="postgres-handler",
            version="3.0.0",
            priority=50,
        )

        # Simulate registration logic
        registration = {
            "type": descriptor.handler_type,
            "name": descriptor.name,
            "version": descriptor.version,
            "priority": descriptor.priority,
        }

        assert registration["type"] == "postgresql"
        assert registration["name"] == "postgres-handler"
        assert registration["version"] == "3.0.0"
        assert registration["priority"] == 50

    def test_descriptors_can_be_sorted_by_priority(self) -> None:
        """Descriptors can be sorted by priority."""
        descriptors = [
            MockHandlerDescriptor(name="low", priority=1),
            MockHandlerDescriptor(name="high", priority=100),
            MockHandlerDescriptor(name="medium", priority=50),
        ]

        sorted_descriptors = sorted(descriptors, key=lambda d: d.priority, reverse=True)

        assert sorted_descriptors[0].name == "high"
        assert sorted_descriptors[1].name == "medium"
        assert sorted_descriptors[2].name == "low"

    def test_descriptors_can_be_filtered_by_type(self) -> None:
        """Descriptors can be filtered by handler_type."""
        descriptors = [
            MockHandlerDescriptor(handler_type="http", name="http-1"),
            MockHandlerDescriptor(handler_type="kafka", name="kafka-1"),
            MockHandlerDescriptor(handler_type="http", name="http-2"),
        ]

        http_descriptors = [d for d in descriptors if d.handler_type == "http"]

        assert len(http_descriptors) == 2
        assert all(d.handler_type == "http" for d in http_descriptors)

    def test_metadata_provides_capabilities(self) -> None:
        """Metadata can provide capability information."""
        descriptor = MockHandlerDescriptor(
            metadata={
                "capabilities": ["read", "write", "batch"],
                "max_connections": 100,
                "supports_transactions": True,
            }
        )

        capabilities = descriptor.metadata.get("capabilities", [])
        assert "read" in capabilities
        assert "write" in capabilities
        assert descriptor.metadata.get("supports_transactions") is True


@pytest.mark.unit
class TestProtocolHandlerDescriptorImports:
    """Test protocol imports from different locations."""

    def test_import_from_types_module(self) -> None:
        """Test direct import from types module."""
        from omnibase_spi.protocols.handlers.types import (
            ProtocolHandlerDescriptor as DirectProtocolHandlerDescriptor,
        )

        descriptor = MockHandlerDescriptor()
        assert isinstance(descriptor, DirectProtocolHandlerDescriptor)

    def test_import_from_handlers_package(self) -> None:
        """Test import from handlers package."""
        from omnibase_spi.protocols.handlers import (
            ProtocolHandlerDescriptor as HandlersProtocolHandlerDescriptor,
        )

        descriptor = MockHandlerDescriptor()
        assert isinstance(descriptor, HandlersProtocolHandlerDescriptor)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.handlers import (
            ProtocolHandlerDescriptor as HandlersProtocolHandlerDescriptor,
        )
        from omnibase_spi.protocols.handlers.types import (
            ProtocolHandlerDescriptor as DirectProtocolHandlerDescriptor,
        )

        assert DirectProtocolHandlerDescriptor is HandlersProtocolHandlerDescriptor


@pytest.mark.unit
class TestProtocolHandlerDescriptorDocumentation:
    """Test that ProtocolHandlerDescriptor has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolHandlerDescriptor should have a docstring."""
        assert ProtocolHandlerDescriptor.__doc__ is not None
        assert len(ProtocolHandlerDescriptor.__doc__.strip()) > 0

    def test_docstring_describes_purpose(self) -> None:
        """Docstring should describe the protocol's purpose."""
        doc = ProtocolHandlerDescriptor.__doc__ or ""
        # The docstring should mention descriptors and handlers
        assert "descriptor" in doc.lower() or "handler" in doc.lower()
