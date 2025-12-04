"""
Tests for ProtocolHandlerRegistry protocol.

Validates that ProtocolHandlerRegistry:
- Is properly runtime checkable
- Defines required methods (register, get, list_protocols, is_registered)
- Methods have correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

import pytest
from typing import Type

from omnibase_spi.protocols.registry.handler_registry import ProtocolHandlerRegistry


class MockHandler:
    """Mock handler for testing."""

    def handle(self) -> str:
        """Mock handle method."""
        return "handled"


class CompliantRegistry:
    """A class that fully implements the ProtocolHandlerRegistry protocol."""

    def __init__(self) -> None:
        """Initialize registry with empty storage."""
        self._handlers: dict[str, Type[object]] = {}

    def register(
        self,
        protocol_type: str,
        handler_cls: Type[object],
    ) -> None:
        """Register a protocol handler."""
        self._handlers[protocol_type] = handler_cls

    def get(
        self,
        protocol_type: str,
    ) -> Type[object]:
        """Get handler class for protocol type."""
        return self._handlers[protocol_type]

    def list_protocols(self) -> list[str]:
        """List registered protocol types."""
        return list(self._handlers.keys())

    def is_registered(self, protocol_type: str) -> bool:
        """Check if protocol type is registered."""
        return protocol_type in self._handlers


class PartialRegistry:
    """A class that only implements some ProtocolHandlerRegistry methods."""

    def register(
        self,
        protocol_type: str,
        handler_cls: Type[object],
    ) -> None:
        """Register a protocol handler."""
        pass

    def get(
        self,
        protocol_type: str,
    ) -> Type[object]:
        """Get handler class for protocol type."""
        return MockHandler


class NonCompliantRegistry:
    """A class that implements none of the ProtocolHandlerRegistry methods."""

    pass


class WrongSignatureRegistry:
    """A class that implements methods with wrong signatures."""

    def register(self, protocol_type: str) -> None:  # Missing handler_cls parameter
        """Register a protocol handler."""
        pass

    def get(self, protocol_type: str) -> Type[object]:
        """Get handler class for protocol type."""
        return MockHandler

    def list_protocols(self) -> list[str]:
        """List registered protocol types."""
        return []

    def is_registered(self, protocol_type: str) -> bool:
        """Check if protocol type is registered."""
        return False


class TestProtocolHandlerRegistryProtocol:
    """Test suite for ProtocolHandlerRegistry protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolHandlerRegistry should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol, older versions use __runtime_protocol__
        assert hasattr(ProtocolHandlerRegistry, "_is_runtime_protocol") or hasattr(
            ProtocolHandlerRegistry, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolHandlerRegistry should be a Protocol class."""
        from typing import Protocol

        # Check that ProtocolHandlerRegistry has Protocol in its bases
        assert any(
            getattr(base, "__name__", "") == "Protocol"
            for base in ProtocolHandlerRegistry.__mro__
        )

    def test_protocol_has_register_method(self) -> None:
        """ProtocolHandlerRegistry should define register method."""
        assert "register" in dir(ProtocolHandlerRegistry)

    def test_protocol_has_get_method(self) -> None:
        """ProtocolHandlerRegistry should define get method."""
        assert "get" in dir(ProtocolHandlerRegistry)

    def test_protocol_has_list_protocols_method(self) -> None:
        """ProtocolHandlerRegistry should define list_protocols method."""
        assert "list_protocols" in dir(ProtocolHandlerRegistry)

    def test_protocol_has_is_registered_method(self) -> None:
        """ProtocolHandlerRegistry should define is_registered method."""
        assert "is_registered" in dir(ProtocolHandlerRegistry)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolHandlerRegistry protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolHandlerRegistry()  # type: ignore[misc]


class TestProtocolHandlerRegistryCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all ProtocolHandlerRegistry methods should pass isinstance check."""
        registry = CompliantRegistry()
        assert isinstance(registry, ProtocolHandlerRegistry)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing ProtocolHandlerRegistry methods should fail isinstance check."""
        registry = PartialRegistry()
        assert not isinstance(registry, ProtocolHandlerRegistry)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no ProtocolHandlerRegistry methods should fail isinstance check."""
        registry = NonCompliantRegistry()
        assert not isinstance(registry, ProtocolHandlerRegistry)

    def test_wrong_signature_still_passes_structural_check(self) -> None:
        """
        A class with methods of wrong signatures still passes isinstance.

        Note: Runtime protocol checking only verifies method existence,
        not signature correctness. Type checking is enforced by static analysis tools.
        """
        registry = WrongSignatureRegistry()
        # Runtime check passes because methods exist
        assert isinstance(registry, ProtocolHandlerRegistry)


class TestProtocolHandlerRegistryMethodSignatures:
    """Test method signatures and behavior from compliant implementations."""

    def test_register_accepts_protocol_type_and_handler_cls(self) -> None:
        """register method should accept protocol_type and handler_cls parameters."""
        registry = CompliantRegistry()
        # Should not raise
        registry.register("http_rest", MockHandler)

    def test_get_returns_handler_class(self) -> None:
        """get method should return a handler class."""
        registry = CompliantRegistry()
        registry.register("http_rest", MockHandler)
        result = registry.get("http_rest")
        assert result is MockHandler

    def test_list_protocols_returns_list_of_strings(self) -> None:
        """list_protocols method should return a list of strings."""
        registry = CompliantRegistry()
        registry.register("http_rest", MockHandler)
        registry.register("bolt", MockHandler)
        result = registry.list_protocols()
        assert isinstance(result, list)
        assert all(isinstance(protocol, str) for protocol in result)
        assert "http_rest" in result
        assert "bolt" in result

    def test_is_registered_returns_bool(self) -> None:
        """is_registered method should return a boolean."""
        registry = CompliantRegistry()
        registry.register("http_rest", MockHandler)
        assert registry.is_registered("http_rest") is True
        assert registry.is_registered("unknown") is False


class TestProtocolHandlerRegistryWorkflow:
    """Test typical workflow using ProtocolHandlerRegistry."""

    def test_complete_registration_workflow(self) -> None:
        """Test complete register, get, list, is_registered workflow."""
        registry = CompliantRegistry()

        # Initially empty
        assert registry.list_protocols() == []
        assert not registry.is_registered("http_rest")

        # Register handler
        registry.register("http_rest", MockHandler)

        # Verify registration
        assert registry.is_registered("http_rest")
        assert "http_rest" in registry.list_protocols()

        # Retrieve handler
        handler_cls = registry.get("http_rest")
        assert handler_cls is MockHandler

    def test_multiple_handler_registration(self) -> None:
        """Test registering multiple handlers."""
        registry = CompliantRegistry()

        class Handler1:
            pass

        class Handler2:
            pass

        registry.register("http_rest", Handler1)
        registry.register("bolt", Handler2)

        assert len(registry.list_protocols()) == 2
        assert registry.get("http_rest") is Handler1
        assert registry.get("bolt") is Handler2


class TestProtocolHandlerRegistryImports:
    """Test protocol imports from different locations."""

    def test_import_from_handler_registry_module(self) -> None:
        """Test direct import from handler_registry module."""
        from omnibase_spi.protocols.registry.handler_registry import (
            ProtocolHandlerRegistry as DirectProtocolHandlerRegistry,
        )

        registry = CompliantRegistry()
        assert isinstance(registry, DirectProtocolHandlerRegistry)

    def test_import_from_registry_package(self) -> None:
        """Test import from registry package."""
        from omnibase_spi.protocols.registry import (
            ProtocolHandlerRegistry as RegistryProtocolHandlerRegistry,
        )

        registry = CompliantRegistry()
        assert isinstance(registry, RegistryProtocolHandlerRegistry)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.registry import (
            ProtocolHandlerRegistry as RegistryProtocolHandlerRegistry,
        )
        from omnibase_spi.protocols.registry.handler_registry import (
            ProtocolHandlerRegistry as DirectProtocolHandlerRegistry,
        )

        assert RegistryProtocolHandlerRegistry is DirectProtocolHandlerRegistry
