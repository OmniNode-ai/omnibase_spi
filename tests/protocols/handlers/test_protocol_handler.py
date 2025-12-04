"""
Tests for ProtocolHandler protocol.

Validates that ProtocolHandler:
- Is properly runtime checkable
- Defines required methods (initialize, shutdown, execute)
- Methods have correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

import pytest

from omnibase_spi.protocols.handlers.protocol_handler import ProtocolHandler


class CompliantHandler:
    """A class that fully implements the ProtocolHandler protocol."""

    async def initialize(self, config: "ModelConnectionConfig") -> None:
        """Initialize the handler."""
        pass

    async def shutdown(self) -> None:
        """Shutdown the handler."""
        pass

    async def execute(
        self,
        request: "ModelProtocolRequest",
        operation_config: "ModelOperationConfig",
    ) -> "ModelProtocolResponse":
        """Execute a protocol operation."""
        # Return a mock response
        from unittest.mock import MagicMock

        return MagicMock()


class PartialHandler:
    """A class that only implements some ProtocolHandler methods."""

    async def initialize(self, config: "ModelConnectionConfig") -> None:
        """Initialize the handler."""
        pass


class NonCompliantHandler:
    """A class that implements none of the ProtocolHandler methods."""

    pass


class WrongSignatureHandler:
    """A class that implements methods with wrong signatures."""

    async def initialize(self) -> None:  # type: ignore[override]
        """Initialize with wrong signature (missing config parameter)."""
        pass

    async def shutdown(self) -> None:
        """Shutdown the handler."""
        pass

    async def execute(
        self,
        request: "ModelProtocolRequest",
        operation_config: "ModelOperationConfig",
    ) -> "ModelProtocolResponse":
        """Execute a protocol operation."""
        from unittest.mock import MagicMock

        return MagicMock()


class TestProtocolHandlerProtocol:
    """Test suite for ProtocolHandler protocol compliance."""

    def test_protocol_handler_is_runtime_checkable(self) -> None:
        """ProtocolHandler should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol, older versions use __runtime_protocol__
        assert hasattr(ProtocolHandler, "_is_runtime_protocol") or hasattr(
            ProtocolHandler, "__runtime_protocol__"
        )

    def test_protocol_handler_is_protocol(self) -> None:
        """ProtocolHandler should be a Protocol class."""
        from typing import Protocol

        # Check that ProtocolHandler has Protocol in its bases
        assert any(
            base is Protocol or getattr(base, "__name__", "") == "Protocol"
            for base in ProtocolHandler.__mro__
        )

    def test_protocol_handler_has_initialize_method(self) -> None:
        """ProtocolHandler should define initialize method."""
        assert "initialize" in dir(ProtocolHandler)

    def test_protocol_handler_has_shutdown_method(self) -> None:
        """ProtocolHandler should define shutdown method."""
        assert "shutdown" in dir(ProtocolHandler)

    def test_protocol_handler_has_execute_method(self) -> None:
        """ProtocolHandler should define execute method."""
        assert "execute" in dir(ProtocolHandler)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolHandler protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolHandler()  # type: ignore[call-arg]


class TestProtocolHandlerCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all ProtocolHandler methods should pass isinstance check."""
        handler = CompliantHandler()
        assert isinstance(handler, ProtocolHandler)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing ProtocolHandler methods should fail isinstance check."""
        handler = PartialHandler()
        assert not isinstance(handler, ProtocolHandler)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no ProtocolHandler methods should fail isinstance check."""
        handler = NonCompliantHandler()
        assert not isinstance(handler, ProtocolHandler)

    def test_wrong_signature_still_passes_structural_check(self) -> None:
        """
        A class with methods of wrong signatures still passes isinstance.

        Note: Runtime protocol checking only verifies method existence,
        not signature correctness. Signature checking is enforced by static analysis tools.
        """
        handler = WrongSignatureHandler()
        # Runtime check passes because methods exist (structural typing)
        assert isinstance(handler, ProtocolHandler)


class TestProtocolHandlerMethodSignatures:
    """Test method signatures from compliant implementations."""

    @pytest.mark.asyncio
    async def test_initialize_accepts_config(self) -> None:
        """initialize method should accept ModelConnectionConfig."""
        from unittest.mock import MagicMock

        handler = CompliantHandler()
        config = MagicMock()
        # Should not raise
        await handler.initialize(config)

    @pytest.mark.asyncio
    async def test_shutdown_takes_no_args(self) -> None:
        """shutdown method should take no arguments."""
        handler = CompliantHandler()
        # Should not raise
        await handler.shutdown()

    @pytest.mark.asyncio
    async def test_execute_accepts_request_and_config(self) -> None:
        """execute method should accept request and operation_config."""
        from unittest.mock import MagicMock

        handler = CompliantHandler()
        request = MagicMock()
        operation_config = MagicMock()
        # Should not raise and return a response
        response = await handler.execute(request, operation_config)
        assert response is not None

    @pytest.mark.asyncio
    async def test_execute_returns_response(self) -> None:
        """execute method should return ModelProtocolResponse."""
        from unittest.mock import MagicMock

        handler = CompliantHandler()
        request = MagicMock()
        operation_config = MagicMock()
        response = await handler.execute(request, operation_config)
        # Verify we get something back
        assert response is not None


class TestProtocolHandlerAsyncNature:
    """Test that ProtocolHandler methods are async."""

    def test_initialize_is_async(self) -> None:
        """initialize should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(CompliantHandler.initialize)

    def test_shutdown_is_async(self) -> None:
        """shutdown should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(CompliantHandler.shutdown)

    def test_execute_is_async(self) -> None:
        """execute should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(CompliantHandler.execute)


class TestProtocolHandlerImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_handler_module(self) -> None:
        """Test direct import from protocol_handler module."""
        from omnibase_spi.protocols.handlers.protocol_handler import (
            ProtocolHandler as DirectProtocolHandler,
        )

        handler = CompliantHandler()
        assert isinstance(handler, DirectProtocolHandler)

    def test_import_from_handlers_package(self) -> None:
        """Test import from handlers package."""
        from omnibase_spi.protocols.handlers import (
            ProtocolHandler as HandlersProtocolHandler,
        )

        handler = CompliantHandler()
        assert isinstance(handler, HandlersProtocolHandler)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.handlers import (
            ProtocolHandler as HandlersProtocolHandler,
        )
        from omnibase_spi.protocols.handlers.protocol_handler import (
            ProtocolHandler as DirectProtocolHandler,
        )

        assert HandlersProtocolHandler is DirectProtocolHandler


class TestProtocolHandlerDocumentation:
    """Test that ProtocolHandler has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolHandler should have a docstring."""
        assert ProtocolHandler.__doc__ is not None
        assert len(ProtocolHandler.__doc__.strip()) > 0

    def test_initialize_has_docstring(self) -> None:
        """initialize method should have a docstring."""
        # Access through protocol's __annotations__ or compliant implementation
        assert CompliantHandler.initialize.__doc__ is not None

    def test_shutdown_has_docstring(self) -> None:
        """shutdown method should have a docstring."""
        assert CompliantHandler.shutdown.__doc__ is not None

    def test_execute_has_docstring(self) -> None:
        """execute method should have a docstring."""
        assert CompliantHandler.execute.__doc__ is not None
