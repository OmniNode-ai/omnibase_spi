"""
Tests for omnibase_spi.exceptions module.

This module provides comprehensive test coverage for the SPI exception hierarchy,
ensuring proper initialization, inheritance, and context handling.
"""

from __future__ import annotations

from typing import Any

import pytest

from omnibase_spi.exceptions import (
    ContractCompilerError,
    HandlerInitializationError,
    IdempotencyStoreError,
    InvalidProtocolStateError,
    ProjectionReadError,
    ProjectorError,
    ProtocolHandlerError,
    ProtocolNotImplementedError,
    RegistryError,
    SPIError,
)


@pytest.mark.unit
class TestSPIError:
    """Tests for the SPIError base exception class."""

    def test_create_with_message_only(self) -> None:
        """Test creating SPIError with just a message."""
        error = SPIError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.context == {}

    def test_create_with_empty_message(self) -> None:
        """Test creating SPIError with empty message."""
        error = SPIError()
        assert str(error) == ""
        assert error.context == {}

    def test_create_with_message_and_context(self) -> None:
        """Test creating SPIError with both message and context."""
        context = {
            "handler_id": "http_handler_123",
            "protocol_type": "http",
            "operation": "execute",
        }
        error = SPIError("Handler execution failed", context=context)
        assert str(error) == "Handler execution failed"
        assert error.context == context
        assert error.context is not context  # Verify it's a copy
        assert error.context["handler_id"] == "http_handler_123"

    def test_context_top_level_is_independent_copy(self) -> None:
        """Test that context is copied at the top level, not stored by reference.

        This verifies that modifying the original context dict after error creation
        does not affect the error's context. For nested object isolation (deep copy),
        see test_context_deep_copy_behavior.
        """
        original_context = {"key": "value"}
        error = SPIError("Test error", context=original_context)

        # Context should be a copy, not the same reference
        assert error.context is not original_context

        # Mutating original should not affect error's context
        original_context["new_key"] = "new_value"
        assert "new_key" not in error.context
        assert error.context == {"key": "value"}

    def test_inherits_from_exception(self) -> None:
        """Test that SPIError inherits from Exception."""
        error = SPIError("Test")
        assert isinstance(error, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        """Test that SPIError can be raised and caught."""
        with pytest.raises(SPIError) as exc_info:
            raise SPIError("Test error", context={"test": True})
        assert str(exc_info.value) == "Test error"
        assert exc_info.value.context == {"test": True}

    def test_context_with_none_becomes_empty_dict(self) -> None:
        """Test that None context is converted to empty dict."""
        error = SPIError("Test", context=None)
        assert error.context == {}
        assert isinstance(error.context, dict)

    def test_context_deep_copy_behavior(self) -> None:
        """Verify that context uses deep copy - nested mutables are fully isolated."""
        nested_list = ["item1"]
        nested_dict = {"inner_key": "inner_value"}
        context: dict[str, Any] = {
            "nested_list": nested_list,
            "nested_dict": nested_dict,
        }
        error = SPIError("Test", context=context)

        # Verify top-level is independent
        context["new_key"] = "value"
        assert "new_key" not in error.context

        # Verify nested list is fully isolated (deep copy)
        nested_list.append("item2")
        assert error.context["nested_list"] == ["item1"]  # Original value preserved

        # Verify nested dict is fully isolated (deep copy)
        nested_dict["another_key"] = "another_value"
        assert "another_key" not in error.context["nested_dict"]
        assert error.context["nested_dict"] == {"inner_key": "inner_value"}


@pytest.mark.unit
class TestProtocolHandlerError:
    """Tests for ProtocolHandlerError."""

    def test_inherits_from_spi_error(self) -> None:
        """Test inheritance chain."""
        error = ProtocolHandlerError("Handler failed")
        assert isinstance(error, SPIError)
        assert isinstance(error, Exception)

    def test_create_with_message_and_context(self) -> None:
        """Test creating with handler-specific context."""
        context = {
            "status_code": 500,
            "url": "https://api.example.com/test",
            "method": "POST",
        }
        error = ProtocolHandlerError("HTTP request failed", context=context)
        assert str(error) == "HTTP request failed"
        assert error.context["status_code"] == 500

    def test_can_be_caught_as_spi_error(self) -> None:
        """Test that ProtocolHandlerError can be caught as SPIError."""
        with pytest.raises(SPIError):
            raise ProtocolHandlerError("Handler error")


@pytest.mark.unit
class TestHandlerInitializationError:
    """Tests for HandlerInitializationError."""

    def test_inherits_from_protocol_handler_error(self) -> None:
        """Test inheritance chain."""
        error = HandlerInitializationError("Init failed")
        assert isinstance(error, ProtocolHandlerError)
        assert isinstance(error, SPIError)
        assert isinstance(error, Exception)

    def test_create_with_connection_context(self) -> None:
        """Test creating with connection-related context."""
        context = {
            "connection_string": "postgres://localhost/db",
            "timeout": 30,
            "retry_count": 3,
        }
        error = HandlerInitializationError(
            "Failed to connect to database", context=context
        )
        assert error.context["timeout"] == 30

    def test_can_be_caught_at_multiple_levels(self) -> None:
        """Test catching at different inheritance levels."""
        # Can catch as HandlerInitializationError
        with pytest.raises(HandlerInitializationError):
            raise HandlerInitializationError("Init failed")

        # Can catch as ProtocolHandlerError
        with pytest.raises(ProtocolHandlerError):
            raise HandlerInitializationError("Init failed")

        # Can catch as SPIError
        with pytest.raises(SPIError):
            raise HandlerInitializationError("Init failed")


@pytest.mark.unit
class TestIdempotencyStoreError:
    """Tests for IdempotencyStoreError."""

    def test_inherits_from_spi_error(self) -> None:
        """Test inheritance chain."""
        error = IdempotencyStoreError("Store error")
        assert isinstance(error, SPIError)

    def test_create_with_event_context(self) -> None:
        """Test creating with event-related context."""
        context = {
            "event_id": "evt-123",
            "idempotency_key": "key-456",
            "operation": "record",
            "store_type": "redis",
        }
        error = IdempotencyStoreError("Failed to record event", context=context)
        assert error.context["event_id"] == "evt-123"
        assert error.context["store_type"] == "redis"


@pytest.mark.unit
class TestContractCompilerError:
    """Tests for ContractCompilerError."""

    def test_inherits_from_spi_error(self) -> None:
        """Test inheritance chain."""
        error = ContractCompilerError("Compilation failed")
        assert isinstance(error, SPIError)

    def test_create_with_contract_context(self) -> None:
        """Test creating with contract-related context."""
        context = {
            "path": "/contracts/effect.yaml",
            "line_number": 42,
            "missing_fields": ["protocol", "version"],
            "contract_type": "effect",
        }
        error = ContractCompilerError(
            "Invalid contract: missing required field", context=context
        )
        assert error.context["line_number"] == 42
        assert "protocol" in error.context["missing_fields"]


@pytest.mark.unit
class TestRegistryError:
    """Tests for RegistryError."""

    def test_inherits_from_spi_error(self) -> None:
        """Test inheritance chain."""
        error = RegistryError("Registry error")
        assert isinstance(error, SPIError)

    def test_create_with_registry_context(self) -> None:
        """Test creating with registry-related context."""
        context = {
            "protocol_type": "http",
            "available_types": ["grpc", "websocket"],
            "operation": "lookup",
        }
        error = RegistryError("Protocol type 'http' is not registered", context=context)
        assert error.context["protocol_type"] == "http"
        assert "grpc" in error.context["available_types"]


@pytest.mark.unit
class TestProtocolNotImplementedError:
    """Tests for ProtocolNotImplementedError."""

    def test_inherits_from_spi_error(self) -> None:
        """Test inheritance chain."""
        error = ProtocolNotImplementedError("Not implemented")
        assert isinstance(error, SPIError)

    def test_create_with_implementation_context(self) -> None:
        """Test creating with implementation-related context."""
        context = {
            "protocol_name": "IEffectNode",
            "required_by": "WorkflowOrchestrator",
            "available_implementations": ["ComputeNode", "ReducerNode"],
        }
        error = ProtocolNotImplementedError(
            "No implementation registered for protocol", context=context
        )
        assert error.context["protocol_name"] == "IEffectNode"
        assert error.context["required_by"] == "WorkflowOrchestrator"


@pytest.mark.unit
class TestInvalidProtocolStateError:
    """Tests for InvalidProtocolStateError."""

    def test_inherits_from_spi_error(self) -> None:
        """Test inheritance chain."""
        error = InvalidProtocolStateError("Invalid state")
        assert isinstance(error, SPIError)

    def test_create_with_lifecycle_context(self) -> None:
        """Test creating with lifecycle-related context."""
        context = {
            "node_id": "node-123",
            "current_state": "uninitialized",
            "required_state": "initialized",
            "operation": "execute",
            "lifecycle_history": ["created", "configured"],
        }
        error = InvalidProtocolStateError(
            "Cannot call execute() before initialize()", context=context
        )
        assert error.context["current_state"] == "uninitialized"
        assert error.context["required_state"] == "initialized"
        assert "created" in error.context["lifecycle_history"]


@pytest.mark.unit
class TestProjectorError:
    """Tests for ProjectorError."""

    def test_inherits_from_spi_error(self) -> None:
        """Test inheritance chain."""
        error = ProjectorError("Projection failed")
        assert isinstance(error, SPIError)

    def test_create_with_projection_context(self) -> None:
        """Test creating with projection-related context."""
        context = {
            "entity_id": "order-456",
            "domain": "orders",
            "sequence": 42,
            "operation": "persist",
            "store_type": "postgres",
        }
        error = ProjectorError("Failed to persist projection", context=context)
        assert error.context["entity_id"] == "order-456"
        assert error.context["sequence"] == 42


@pytest.mark.unit
class TestProjectionReadError:
    """Tests for ProjectionReadError."""

    def test_inherits_from_spi_error(self) -> None:
        """Test inheritance chain."""
        error = ProjectionReadError("Read failed")
        assert isinstance(error, SPIError)

    def test_create_with_read_context(self) -> None:
        """Test creating with read operation context."""
        context = {
            "entity_id": "order-789",
            "domain": "orders",
            "operation": "get_entity_state",
        }
        error = ProjectionReadError("Failed to query projection", context=context)
        assert error.context["entity_id"] == "order-789"
        assert error.context["operation"] == "get_entity_state"


@pytest.mark.unit
class TestExceptionHierarchy:
    """Tests for the complete exception hierarchy."""

    def test_all_exceptions_inherit_from_spi_error(self) -> None:
        """Verify all SPI exceptions inherit from SPIError."""
        exception_classes: list[type[SPIError]] = [
            ProtocolHandlerError,
            HandlerInitializationError,
            IdempotencyStoreError,
            ContractCompilerError,
            RegistryError,
            ProtocolNotImplementedError,
            InvalidProtocolStateError,
            ProjectorError,
            ProjectionReadError,
        ]
        for exc_class in exception_classes:
            error = exc_class("Test")
            assert isinstance(
                error, SPIError
            ), f"{exc_class.__name__} should inherit from SPIError"

    def test_handler_initialization_error_inheritance(self) -> None:
        """Verify HandlerInitializationError has two-level inheritance."""
        error = HandlerInitializationError("Test")
        assert isinstance(error, HandlerInitializationError)
        assert isinstance(error, ProtocolHandlerError)
        assert isinstance(error, SPIError)
        assert isinstance(error, Exception)

    def test_broad_exception_handling(self) -> None:
        """Test that SPIError can catch any SPI exception."""
        exceptions_to_test: list[SPIError] = [
            ProtocolHandlerError("handler error"),
            HandlerInitializationError("init error"),
            IdempotencyStoreError("store error"),
            ContractCompilerError("compiler error"),
            RegistryError("registry error"),
            ProtocolNotImplementedError("not implemented"),
            InvalidProtocolStateError("invalid state"),
            ProjectorError("projector error"),
            ProjectionReadError("read error"),
        ]

        for exc in exceptions_to_test:
            with pytest.raises(SPIError) as exc_info:
                raise exc
            assert exc_info.value is exc

    def test_context_preserved_through_inheritance(self) -> None:
        """Test that context is properly passed through inheritance."""
        context = {"key": "value", "number": 42}

        # Test at each level of deepest inheritance chain
        error1 = HandlerInitializationError("Test", context=context)
        assert error1.context == context

        # Catch as parent and verify context still accessible
        try:
            raise HandlerInitializationError("Test", context=context)
        except ProtocolHandlerError as e:
            assert e.context == context


@pytest.mark.unit
class TestExceptionReprStr:
    """Tests for exception string representations."""

    def test_str_returns_message(self) -> None:
        """Test __str__ returns the error message."""
        error = SPIError("Something went wrong")
        assert str(error) == "Something went wrong"

    def test_str_empty_message(self) -> None:
        """Test __str__ with empty message."""
        error = SPIError()
        assert str(error) == ""

    def test_repr_includes_class_and_message(self) -> None:
        """Test __repr__ includes class name and message."""
        error = SPIError("Test error")
        r = repr(error)
        assert "SPIError" in r
        assert "Test error" in r

    def test_repr_subclass_shows_correct_class(self) -> None:
        """Test __repr__ for subclasses shows correct class name."""
        error = ProtocolHandlerError("Handler failed")
        r = repr(error)
        assert "ProtocolHandlerError" in r
        assert "Handler failed" in r

    def test_repr_with_context(self) -> None:
        """Test __repr__ works with context."""
        error = SPIError("Error", context={"key": "value"})
        r = repr(error)
        assert "SPIError" in r

    def test_repr_for_all_exception_types(self) -> None:
        """Test __repr__ works correctly for all exception subclasses."""
        exception_instances: list[tuple[SPIError, str]] = [
            (ProtocolHandlerError("handler msg"), "ProtocolHandlerError"),
            (HandlerInitializationError("init msg"), "HandlerInitializationError"),
            (IdempotencyStoreError("store msg"), "IdempotencyStoreError"),
            (ContractCompilerError("compiler msg"), "ContractCompilerError"),
            (RegistryError("registry msg"), "RegistryError"),
            (
                ProtocolNotImplementedError("not impl msg"),
                "ProtocolNotImplementedError",
            ),
            (InvalidProtocolStateError("state msg"), "InvalidProtocolStateError"),
            (ProjectorError("projector msg"), "ProjectorError"),
            (ProjectionReadError("read msg"), "ProjectionReadError"),
        ]
        for error, expected_class_name in exception_instances:
            r = repr(error)
            assert expected_class_name in r, f"{expected_class_name} not in repr: {r}"

    def test_str_for_subclass(self) -> None:
        """Test __str__ works correctly for subclasses."""
        error = HandlerInitializationError("Initialization failed")
        assert str(error) == "Initialization failed"


@pytest.mark.unit
class TestExceptionChaining:
    """Tests for exception chaining with 'raise ... from e' pattern.

    Exception chaining is a Python feature that preserves the original cause
    of an exception when re-raising. This is critical for debugging and
    error tracing in complex systems.
    """

    def test_spi_error_chaining_preserves_cause(self) -> None:
        """Test that raise SPIError from e preserves __cause__."""
        original = ValueError("Original error")
        chained = SPIError("Wrapped error")
        chained.__cause__ = original

        assert chained.__cause__ is original
        assert isinstance(chained.__cause__, ValueError)
        assert str(chained.__cause__) == "Original error"

    def test_spi_error_chaining_via_raise_from(self) -> None:
        """Test exception chaining using raise ... from syntax."""
        original = ValueError("Original error")

        with pytest.raises(SPIError) as exc_info:
            try:
                raise original
            except ValueError as e:
                raise SPIError("Wrapped error") from e

        assert exc_info.value.__cause__ is original
        assert str(exc_info.value.__cause__) == "Original error"

    def test_registry_error_chaining(self) -> None:
        """Test exception chaining for RegistryError."""
        original = KeyError("handler_type")

        with pytest.raises(RegistryError) as exc_info:
            try:
                raise original
            except KeyError as e:
                raise RegistryError(
                    "Protocol type not found",
                    context={"protocol_type": "unknown"},
                ) from e

        assert exc_info.value.__cause__ is original
        assert exc_info.value.context["protocol_type"] == "unknown"

    def test_contract_compiler_error_chaining(self) -> None:
        """Test exception chaining for ContractCompilerError."""
        original = FileNotFoundError("contract.yaml")

        with pytest.raises(ContractCompilerError) as exc_info:
            try:
                raise original
            except FileNotFoundError as e:
                raise ContractCompilerError(
                    "Failed to load contract file",
                    context={"path": "contract.yaml"},
                ) from e

        assert exc_info.value.__cause__ is original
        assert isinstance(exc_info.value.__cause__, FileNotFoundError)

    def test_handler_initialization_error_chaining(self) -> None:
        """Test exception chaining for HandlerInitializationError."""
        original = ConnectionError("Database connection refused")

        with pytest.raises(HandlerInitializationError) as exc_info:
            try:
                raise original
            except ConnectionError as e:
                raise HandlerInitializationError(
                    "Handler failed to initialize",
                    context={"connection_string": "postgres://localhost/db"},
                ) from e

        assert exc_info.value.__cause__ is original
        assert isinstance(exc_info.value.__cause__, ConnectionError)
        # Verify caught at parent level still has cause
        assert exc_info.value.__cause__ is original

    def test_protocol_handler_error_chaining(self) -> None:
        """Test exception chaining for ProtocolHandlerError."""
        original = TimeoutError("Request timed out")

        with pytest.raises(ProtocolHandlerError) as exc_info:
            try:
                raise original
            except TimeoutError as e:
                raise ProtocolHandlerError(
                    "HTTP request failed",
                    context={"timeout": 30, "url": "https://api.example.com"},
                ) from e

        assert exc_info.value.__cause__ is original

    def test_idempotency_store_error_chaining(self) -> None:
        """Test exception chaining for IdempotencyStoreError."""
        original = RuntimeError("Redis connection lost")

        with pytest.raises(IdempotencyStoreError) as exc_info:
            try:
                raise original
            except RuntimeError as e:
                raise IdempotencyStoreError(
                    "Failed to check idempotency",
                    context={"event_id": "evt-123"},
                ) from e

        assert exc_info.value.__cause__ is original

    def test_protocol_not_implemented_error_chaining(self) -> None:
        """Test exception chaining for ProtocolNotImplementedError."""
        original = ImportError("Module not found")

        with pytest.raises(ProtocolNotImplementedError) as exc_info:
            try:
                raise original
            except ImportError as e:
                raise ProtocolNotImplementedError(
                    "No implementation available",
                    context={"protocol_name": "IEffectNode"},
                ) from e

        assert exc_info.value.__cause__ is original

    def test_invalid_protocol_state_error_chaining(self) -> None:
        """Test exception chaining for InvalidProtocolStateError."""
        original = AssertionError("State invariant violated")

        with pytest.raises(InvalidProtocolStateError) as exc_info:
            try:
                raise original
            except AssertionError as e:
                raise InvalidProtocolStateError(
                    "Cannot execute in current state",
                    context={"current_state": "uninitialized"},
                ) from e

        assert exc_info.value.__cause__ is original

    def test_projector_error_chaining(self) -> None:
        """Test exception chaining for ProjectorError."""
        original = OSError("Disk write failed")

        with pytest.raises(ProjectorError) as exc_info:
            try:
                raise original
            except OSError as e:
                raise ProjectorError(
                    "Failed to persist projection",
                    context={"entity_id": "order-456"},
                ) from e

        assert exc_info.value.__cause__ is original

    def test_projection_read_error_chaining(self) -> None:
        """Test exception chaining for ProjectionReadError."""
        original = TimeoutError("Database query timeout")

        with pytest.raises(ProjectionReadError) as exc_info:
            try:
                raise original
            except TimeoutError as e:
                raise ProjectionReadError(
                    "Failed to read projection",
                    context={"entity_id": "order-789"},
                ) from e

        assert exc_info.value.__cause__ is original

    def test_chaining_spi_to_spi_error(self) -> None:
        """Test chaining one SPI error to another SPI error."""
        original = RegistryError("Handler not found")

        with pytest.raises(ProtocolHandlerError) as exc_info:
            try:
                raise original
            except RegistryError as e:
                raise ProtocolHandlerError(
                    "Cannot execute: handler lookup failed"
                ) from e

        assert exc_info.value.__cause__ is original
        assert isinstance(exc_info.value.__cause__, RegistryError)

    def test_multi_level_chaining(self) -> None:
        """Test multiple levels of exception chaining."""
        level1 = ValueError("Invalid value")
        level2 = RegistryError("Registry lookup failed")
        level2.__cause__ = level1
        level3 = ProtocolHandlerError("Handler execution failed")
        level3.__cause__ = level2

        # Verify the chain
        assert level3.__cause__ is level2
        assert level3.__cause__.__cause__ is level1
        assert isinstance(level3.__cause__, RegistryError)
        assert isinstance(level3.__cause__.__cause__, ValueError)

    def test_chaining_with_none_cause(self) -> None:
        """Test that __cause__ is None when not using chaining."""
        error = SPIError("Simple error")
        assert error.__cause__ is None

    def test_chaining_preserves_context(self) -> None:
        """Test that context is preserved alongside cause."""
        original = ValueError("Original")
        context = {"operation": "validate", "field": "email"}

        with pytest.raises(SPIError) as exc_info:
            try:
                raise original
            except ValueError as e:
                raise SPIError("Validation failed", context=context) from e

        # Both cause and context should be preserved
        assert exc_info.value.__cause__ is original
        assert exc_info.value.context == context

    def test_cause_accessible_when_caught_as_parent_type(self) -> None:
        """Test that __cause__ is accessible when catching as parent exception type."""
        original = KeyError("missing_key")

        try:
            try:
                raise original
            except KeyError as e:
                raise HandlerInitializationError("Init failed") from e
        except SPIError as e:
            # Even when caught as SPIError, cause should be accessible
            assert e.__cause__ is original
            assert isinstance(e.__cause__, KeyError)

    def test_suppress_context_with_from_none(self) -> None:
        """Test that 'raise ... from None' suppresses context."""
        with pytest.raises(SPIError) as exc_info:
            try:
                raise ValueError("Original")
            except ValueError:
                raise SPIError("New error without context chain") from None

        assert exc_info.value.__cause__ is None
        # __suppress_context__ is set to True with 'from None'
        assert exc_info.value.__suppress_context__ is True
