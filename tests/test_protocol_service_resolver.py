"""
Test ProtocolServiceResolver protocol import and structure.

Validates that ProtocolServiceResolver follows ONEX SPI protocol design principles
and can be properly imported and used for service resolution.
"""

import sys
from pathlib import Path
from typing import Any, Protocol, get_type_hints

# Add src directory to Python path for testing
src_dir = Path(__file__).parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from omnibase_spi.protocols.container import ProtocolServiceResolver


def test_protocol_service_resolver_import() -> None:
    """Test that ProtocolServiceResolver can be imported."""
    assert ProtocolServiceResolver is not None
    assert isinstance(ProtocolServiceResolver, type)


def test_protocol_service_resolver_is_protocol() -> None:
    """Test that ProtocolServiceResolver is a proper Protocol."""
    # Check that it's defined as a Protocol
    assert issubclass(ProtocolServiceResolver, Protocol)


def test_protocol_service_resolver_is_runtime_checkable() -> None:
    """Test that ProtocolServiceResolver is runtime checkable."""
    # The @runtime_checkable decorator adds __protocol_attrs__
    assert hasattr(ProtocolServiceResolver, "__protocol_attrs__")


def test_protocol_service_resolver_has_get_service_method() -> None:
    """Test that ProtocolServiceResolver defines get_service method."""
    # Check method exists in protocol
    assert hasattr(ProtocolServiceResolver, "get_service")

    # Get method signature through type hints
    hints = get_type_hints(ProtocolServiceResolver.get_service)

    # Verify return type hint exists
    assert "return" in hints


def test_protocol_service_resolver_get_service_signature() -> None:
    """Test that get_service method has correct signature."""
    import inspect

    # Get the method signature
    sig = inspect.signature(ProtocolServiceResolver.get_service)

    # Check parameters
    params = list(sig.parameters.keys())

    # Should have protocol_type_or_name and service_name parameters
    assert "protocol_type_or_name" in params
    assert "service_name" in params

    # Check service_name has default value
    assert sig.parameters["service_name"].default is None


def test_protocol_service_resolver_mock_implementation() -> None:
    """Test that a mock implementation satisfies the protocol."""

    class MockServiceResolver:
        """Mock implementation for testing protocol compliance."""

        def get_service(
            self, protocol_type_or_name: type | str, _service_name: str | None = None
        ) -> Any:
            """Mock get_service implementation."""
            if isinstance(protocol_type_or_name, str):
                return {"service_name": protocol_type_or_name}
            return {"protocol_type": str(protocol_type_or_name)}

    # Create mock instance
    mock_resolver = MockServiceResolver()

    # Verify it satisfies the protocol
    assert isinstance(mock_resolver, ProtocolServiceResolver)


def test_protocol_service_resolver_usage_patterns() -> None:
    """Test that protocol supports expected usage patterns."""

    class TestServiceResolver:
        """Test implementation demonstrating usage patterns."""

        def get_service(
            self, protocol_type_or_name: type | str, service_name: str | None = None
        ) -> Any:
            """Test implementation of get_service."""
            # Pattern 1: String name resolution
            if isinstance(protocol_type_or_name, str) and service_name is None:
                return f"service_{protocol_type_or_name}"

            # Pattern 2: Protocol type resolution
            if hasattr(protocol_type_or_name, "__name__"):
                protocol_name = protocol_type_or_name.__name__
                if service_name:
                    return f"{protocol_name}_{service_name}"
                return protocol_name

            return None

    resolver = TestServiceResolver()

    # Test pattern 1: string name resolution
    result1 = resolver.get_service("cache_service")
    assert result1 == "service_cache_service"

    # Test pattern 2: type resolution
    class ProtocolExample:
        __name__ = "ProtocolExample"

    result2 = resolver.get_service(ProtocolExample)  # type: ignore[arg-type]
    assert result2 == "ProtocolExample"

    # Test pattern 3: type + name resolution
    result3 = resolver.get_service(ProtocolExample, "specific_instance")  # type: ignore[arg-type]
    assert result3 == "ProtocolExample_specific_instance"


def test_protocol_service_resolver_container_export() -> None:
    """Test that ProtocolServiceResolver is exported from container module."""
    from omnibase_spi.protocols.container import ProtocolServiceResolver as Exported

    assert Exported is ProtocolServiceResolver


def test_protocol_service_resolver_in_container_all() -> None:
    """Test that ProtocolServiceResolver is in container __all__."""
    from omnibase_spi.protocols import container

    assert "ProtocolServiceResolver" in container.__all__


def test_protocol_service_resolver_docstring() -> None:
    """Test that ProtocolServiceResolver has comprehensive documentation."""
    assert ProtocolServiceResolver.__doc__ is not None
    assert len(ProtocolServiceResolver.__doc__) > 100

    # Check for key documentation elements
    doc = ProtocolServiceResolver.__doc__
    assert "service resolution" in doc.lower()
    assert "protocol" in doc.lower()


def test_protocol_service_resolver_method_docstring() -> None:
    """Test that get_service method has comprehensive documentation."""
    assert ProtocolServiceResolver.get_service.__doc__ is not None
    doc = ProtocolServiceResolver.get_service.__doc__

    # Check for key documentation elements
    assert "Args:" in doc
    assert "Returns:" in doc
    assert "protocol_type_or_name" in doc
    assert "service_name" in doc
