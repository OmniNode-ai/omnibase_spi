"""
Test suite for ProtocolContainer protocol.

Validates that ProtocolContainer:
- Is properly runtime checkable
- Works with Generic type parameters
- Can be implemented by concrete classes
- Follows SPI purity rules
"""

from typing import Any, Generic, TypeVar

import pytest

from omnibase_spi.protocols.container import ProtocolContainer

T = TypeVar("T")


class ConcreteContainer(Generic[T]):
    """Concrete implementation of ProtocolContainer for testing."""

    def __init__(self, value: T, metadata: dict[str, Any] | None = None):
        """Initialize container with value and metadata."""
        self._value = value
        self._metadata = metadata or {}

    @property
    def value(self) -> T:
        """Get the wrapped value."""
        return self._value

    @property
    def metadata(self) -> dict[str, Any]:
        """Get container metadata."""
        return self._metadata.copy()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get specific metadata field."""
        return self._metadata.get(key, default)


class TestProtocolContainer:
    """Test suite for ProtocolContainer protocol."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """Verify protocol is runtime checkable."""
        container = ConcreteContainer(value="test", metadata={"source": "api"})
        assert isinstance(container, ProtocolContainer)

    def test_protocol_with_string_type(self) -> None:
        """Test protocol with string type parameter."""
        container: ProtocolContainer[str] = ConcreteContainer(
            value="hello", metadata={"lang": "en"}
        )

        assert container.value == "hello"
        assert container.get_metadata("lang") == "en"
        assert container.get_metadata("missing", "default") == "default"

    def test_protocol_with_int_type(self) -> None:
        """Test protocol with int type parameter."""
        container: ProtocolContainer[int] = ConcreteContainer(
            value=42, metadata={"unit": "count"}
        )

        assert container.value == 42
        assert container.get_metadata("unit") == "count"

    def test_protocol_with_dict_type(self) -> None:
        """Test protocol with complex type parameter."""
        data = {"key": "value", "count": 123}
        container: ProtocolContainer[dict[str, Any]] = ConcreteContainer(
            value=data, metadata={"source": "cache", "ttl": 300}
        )

        assert container.value == data
        assert container.get_metadata("source") == "cache"
        assert container.get_metadata("ttl") == 300

    def test_metadata_returns_copy(self) -> None:
        """Verify metadata returns a copy to prevent external mutation."""
        original_metadata = {"key": "value"}
        container = ConcreteContainer(value="test", metadata=original_metadata)

        # Get metadata and modify it
        metadata = container.metadata
        metadata["key"] = "modified"
        metadata["new_key"] = "new_value"

        # Original should be unchanged
        assert container.get_metadata("key") == "value"
        assert container.get_metadata("new_key") is None

    def test_empty_metadata(self) -> None:
        """Test container with no metadata."""
        container: ProtocolContainer[str] = ConcreteContainer(value="test")

        assert container.value == "test"
        assert container.metadata == {}
        assert container.get_metadata("any_key") is None
        assert container.get_metadata("any_key", "default") == "default"

    def test_default_values(self) -> None:
        """Test get_metadata with various default values."""
        container: ProtocolContainer[str] = ConcreteContainer(
            value="test", metadata={"existing": "value"}
        )

        # Test with None default (implicit)
        assert container.get_metadata("missing") is None

        # Test with string default
        assert container.get_metadata("missing", "default") == "default"

        # Test with numeric default
        assert container.get_metadata("missing", 42) == 42

        # Test with dict default
        default_dict = {"nested": "value"}
        assert container.get_metadata("missing", default_dict) == default_dict

    def test_protocol_covariance(self) -> None:
        """Test that protocol supports covariant type relationships."""
        # This tests that a Container[str] can be treated as Container[object]
        # due to covariance, which is appropriate for read-only properties
        str_container: ProtocolContainer[str] = ConcreteContainer(value="test")
        obj_container: ProtocolContainer[object] = str_container

        # Both should return the same value
        assert str_container.value == "test"
        assert obj_container.value == "test"

    def test_protocol_with_none_value(self) -> None:
        """Test container can wrap None values."""
        container: ProtocolContainer[None] = ConcreteContainer(
            value=None, metadata={"nullable": True}
        )

        assert container.value is None
        assert container.get_metadata("nullable") is True

    def test_protocol_with_optional_type(self) -> None:
        """Test container with optional type parameter."""
        container: ProtocolContainer[str | None] = ConcreteContainer(
            value=None, metadata={"status": "empty"}
        )

        assert container.value is None
        assert container.get_metadata("status") == "empty"

    def test_multiple_containers_independence(self) -> None:
        """Test that multiple containers maintain independent state."""
        container1: ProtocolContainer[str] = ConcreteContainer(
            value="first", metadata={"id": 1}
        )
        container2: ProtocolContainer[str] = ConcreteContainer(
            value="second", metadata={"id": 2}
        )

        assert container1.value == "first"
        assert container2.value == "second"
        assert container1.get_metadata("id") == 1
        assert container2.get_metadata("id") == 2


class TestProtocolContainerImports:
    """Test protocol imports from different locations."""

    def test_import_from_container_module(self) -> None:
        """Test import from container module."""
        from omnibase_spi.protocols.container import ProtocolContainer as PC

        container = ConcreteContainer(value="test")
        assert isinstance(container, PC)

    def test_import_from_protocols_root(self) -> None:
        """Test import from protocols root."""
        from omnibase_spi.protocols import ProtocolContainer as PC

        container = ConcreteContainer(value="test")
        assert isinstance(container, PC)

    def test_both_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols import ProtocolContainer as PC1
        from omnibase_spi.protocols.container import ProtocolContainer as PC2

        assert PC1 is PC2
