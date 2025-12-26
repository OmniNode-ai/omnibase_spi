"""
Unit tests for SPI exception handling patterns.

This module contains unit tests that validate single-component exception behavior.
Each test class focuses on one mock implementation demonstrating proper
exception usage patterns.

Test Categories:
    1. Handler lifecycle exceptions (single handler)
    2. Registry exceptions (single registry)
    3. Exception propagation through hierarchy
    4. Idempotency store exceptions (single store)
    5. Projector exceptions (single projector)
    6. Contract compiler exceptions (single compiler)
    7. Exception recovery patterns (single-component focused)

For multi-component integration tests, see:
    tests/integration/test_exception_integration.py
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

# Import shared mock classes from tests/conftest.py
from tests.conftest import (
    MockConnectionConfig,
    MockOperationConfig,
    MockProtocolRequest,
    MockProtocolResponse,
    RealisticHandlerRegistry,
    RealisticIdempotencyStore,
    RealisticProjector,
    RealisticProtocolHandler,
)

# =============================================================================
# Local Mock Implementations (only used in this test file)
# =============================================================================


class MockHandler:
    """Simple mock handler class for registry testing."""

    pass


class RealisticContractCompiler:
    """
    A realistic contract compiler that demonstrates proper exception usage.

    This compiler shows how to use ContractCompilerError for contract
    validation and compilation failures.

    Exception Usage:
        - ContractCompilerError: Parse errors, validation errors
    """

    def compile(self, contract_yaml: str, path: str = "unknown") -> dict[str, Any]:
        """
        Compile a YAML contract string.

        Args:
            contract_yaml: YAML contract content.
            path: File path for error reporting.

        Returns:
            Compiled contract as dictionary.

        Raises:
            ContractCompilerError: If compilation fails.
        """
        # Simulate validation checks
        if not contract_yaml.strip():
            raise ContractCompilerError(
                "Empty contract file",
                context={
                    "path": path,
                    "error_type": "empty_file",
                    "operation": "compile",
                },
            )

        required_fields = ["protocol", "version"]
        missing_fields = [
            field for field in required_fields if field not in contract_yaml
        ]

        if missing_fields:
            raise ContractCompilerError(
                "Invalid contract: missing required fields",
                context={
                    "path": path,
                    "missing_fields": missing_fields,
                    "required_fields": required_fields,
                    "contract_type": "effect",
                    "operation": "validate",
                },
            )

        # Return mock compiled result
        return {"compiled": True, "source": path}


# =============================================================================
# Unit Tests
# =============================================================================


@pytest.mark.unit
class TestHandlerLifecycleExceptions:
    """
    Unit tests for handler lifecycle exception handling.

    These tests demonstrate how to properly handle exceptions during
    handler initialization, execution, and shutdown phases.
    """

    @pytest.mark.asyncio
    async def test_initialization_failure_raises_handler_initialization_error(
        self,
    ) -> None:
        """
        Handler initialization failure should raise HandlerInitializationError.

        Pattern: Use HandlerInitializationError when connection setup fails.
        This allows callers to distinguish between initialization errors
        and execution errors for proper retry and fallback logic.
        """
        handler = RealisticProtocolHandler(simulate_init_failure=True)
        config = MockConnectionConfig(url="http://failing-host:8080")

        with pytest.raises(HandlerInitializationError) as exc_info:
            await handler.initialize(config)

        # Verify exception contains useful debugging context
        assert "failing-host" in str(exc_info.value)
        assert exc_info.value.context["handler_id"] == "mock-handler-v1"
        assert exc_info.value.context["url"] == "http://failing-host:8080"
        assert exc_info.value.context["operation"] == "initialize"

    @pytest.mark.asyncio
    async def test_invalid_config_raises_handler_initialization_error(self) -> None:
        """
        Invalid configuration should raise HandlerInitializationError.

        Pattern: Validate configuration during initialization and provide
        detailed context about what was invalid.
        """
        handler = RealisticProtocolHandler()
        invalid_config = MockConnectionConfig(valid=False)

        with pytest.raises(HandlerInitializationError) as exc_info:
            await handler.initialize(invalid_config)

        assert "validation_errors" in exc_info.value.context
        assert len(exc_info.value.context["validation_errors"]) > 0

    @pytest.mark.asyncio
    async def test_execute_before_initialize_raises_invalid_protocol_state_error(
        self,
    ) -> None:
        """
        Calling execute() before initialize() should raise InvalidProtocolStateError.

        Pattern: Enforce proper lifecycle by checking state before operations.
        This prevents confusing errors from occurring deep in the handler logic.
        """
        handler = RealisticProtocolHandler()
        request = MockProtocolRequest(operation="query")
        config = MockOperationConfig()

        with pytest.raises(InvalidProtocolStateError) as exc_info:
            await handler.execute(request, config)

        assert exc_info.value.context["current_state"] == "uninitialized"
        assert exc_info.value.context["required_state"] == "initialized"
        assert exc_info.value.context["operation"] == "execute"

    @pytest.mark.asyncio
    async def test_execute_after_shutdown_raises_invalid_protocol_state_error(
        self,
    ) -> None:
        """
        Calling execute() after shutdown() should raise InvalidProtocolStateError.

        Pattern: Closed handlers should not be reused. Always create a
        new handler instance after shutdown.
        """
        handler = RealisticProtocolHandler()
        config = MockConnectionConfig()
        await handler.initialize(config)
        await handler.shutdown()

        request = MockProtocolRequest()
        op_config = MockOperationConfig()

        with pytest.raises(InvalidProtocolStateError) as exc_info:
            await handler.execute(request, op_config)

        assert exc_info.value.context["current_state"] == "shutdown"

    @pytest.mark.asyncio
    async def test_reinitialize_after_shutdown_raises_invalid_protocol_state_error(
        self,
    ) -> None:
        """
        Reinitializing a shutdown handler should raise InvalidProtocolStateError.

        Pattern: Shutdown is a terminal state. Create new instances instead
        of trying to reinitialize.
        """
        handler = RealisticProtocolHandler()
        config = MockConnectionConfig()
        await handler.initialize(config)
        await handler.shutdown()

        with pytest.raises(InvalidProtocolStateError) as exc_info:
            await handler.initialize(config)

        assert "Cannot initialize a shutdown handler" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execution_timeout_raises_protocol_handler_error(self) -> None:
        """
        Operation timeout should raise ProtocolHandlerError.

        Pattern: Use ProtocolHandlerError for runtime execution failures.
        Include timeout value and error type in context.
        """
        handler = RealisticProtocolHandler(simulate_timeout=True)
        config = MockConnectionConfig()
        await handler.initialize(config)

        request = MockProtocolRequest(operation="slow_query")
        op_config = MockOperationConfig(timeout=5.0)

        with pytest.raises(ProtocolHandlerError) as exc_info:
            await handler.execute(request, op_config)

        assert exc_info.value.context["error_type"] == "timeout"
        assert exc_info.value.context["timeout"] == 5.0

    @pytest.mark.asyncio
    async def test_execution_failure_raises_protocol_handler_error(self) -> None:
        """
        Backend service failure should raise ProtocolHandlerError.

        Pattern: Wrap backend errors in ProtocolHandlerError with context
        that helps diagnose the issue without exposing sensitive details.
        """
        handler = RealisticProtocolHandler(simulate_execute_failure=True)
        config = MockConnectionConfig()
        await handler.initialize(config)

        request = MockProtocolRequest()
        op_config = MockOperationConfig()

        with pytest.raises(ProtocolHandlerError) as exc_info:
            await handler.execute(request, op_config)

        assert exc_info.value.context["error_type"] == "service_unavailable"
        assert exc_info.value.context["status_code"] == 503


@pytest.mark.unit
class TestRegistryExceptions:
    """
    Unit tests for registry exception handling.

    These tests demonstrate how to properly handle exceptions during
    handler registration and lookup operations.
    """

    def test_lookup_unregistered_handler_raises_registry_error(self) -> None:
        """
        Looking up an unregistered handler should raise RegistryError.

        Pattern: Provide helpful context including available handlers
        to help users identify typos or missing registrations.
        """
        registry = RealisticHandlerRegistry()
        registry.register("http", MockHandler)

        with pytest.raises(RegistryError) as exc_info:
            registry.get("kafka")

        assert exc_info.value.context["protocol_type"] == "kafka"
        assert "http" in exc_info.value.context["available_types"]
        assert exc_info.value.context["operation"] == "lookup"

    def test_empty_registry_lookup_raises_registry_error_with_suggestion(self) -> None:
        """
        Looking up in empty registry should provide appropriate suggestion.

        Pattern: Customize error messages based on registry state to
        provide actionable guidance.
        """
        registry = RealisticHandlerRegistry()

        with pytest.raises(RegistryError) as exc_info:
            registry.get("http")

        assert exc_info.value.context["available_types"] == []
        assert "No handlers registered" in exc_info.value.context["suggestion"]

    def test_duplicate_registration_raises_registry_error(self) -> None:
        """
        Duplicate registration should raise RegistryError when not allowed.

        Pattern: Include both existing and new handler names in context
        to help identify the conflict.
        """
        registry = RealisticHandlerRegistry(allow_overwrites=False)

        class Handler1:
            pass

        class Handler2:
            pass

        registry.register("http", Handler1)

        with pytest.raises(RegistryError) as exc_info:
            registry.register("http", Handler2)

        assert exc_info.value.context["existing_handler"] == "Handler1"
        assert exc_info.value.context["new_handler"] == "Handler2"
        assert exc_info.value.context["allow_overwrites"] is False

    def test_missing_implementation_raises_protocol_not_implemented_error(self) -> None:
        """
        Missing protocol implementation should raise ProtocolNotImplementedError.

        Pattern: Use ProtocolNotImplementedError when the absence represents
        a missing feature, not just a lookup failure. This distinction
        helps differentiate between configuration errors and missing features.
        """
        registry = RealisticHandlerRegistry()
        registry.register("http", MockHandler)

        with pytest.raises(ProtocolNotImplementedError) as exc_info:
            registry.get_or_raise_not_implemented("grpc")

        assert exc_info.value.context["protocol_name"] == "grpc"
        assert "http" in exc_info.value.context["available_implementations"]


@pytest.mark.unit
class TestExceptionPropagation:
    """
    Unit tests for exception propagation through protocol layers.

    These tests demonstrate how exceptions propagate and should be
    caught at different layers of the application.
    """

    @pytest.mark.asyncio
    async def test_handler_error_caught_as_spi_error(self) -> None:
        """
        All SPI exceptions should be catchable as SPIError.

        Pattern: Use SPIError as a catch-all when you want to handle
        any SPI-related error uniformly, such as in middleware or
        error-handling decorators.
        """
        handler = RealisticProtocolHandler(simulate_init_failure=True)
        config = MockConnectionConfig()

        with pytest.raises(SPIError):
            await handler.initialize(config)

    @pytest.mark.asyncio
    async def test_layered_exception_handling(self) -> None:
        """
        Demonstrate layered exception handling pattern.

        Pattern: Catch specific exceptions first for specific handling,
        then fall back to broader exception types for general error handling.

        Note: In this test, the SPIError catch-all branch is included to
        demonstrate the complete recommended pattern, but is not exercised
        because RealisticProtocolHandler only raises ProtocolHandlerError.
        See test_spi_error_fallback_handler and
        test_spi_error_fallback_with_contract_compiler_error for tests that
        exercise the SPIError fallback with RegistryError and
        ContractCompilerError respectively.
        """
        handler = RealisticProtocolHandler(simulate_timeout=True)
        config = MockConnectionConfig()
        await handler.initialize(config)

        request = MockProtocolRequest()
        op_config = MockOperationConfig()

        error_handled_by: str | None = None

        try:
            await handler.execute(request, op_config)
        except InvalidProtocolStateError:
            # Handle state errors specifically
            error_handled_by = "InvalidProtocolStateError"
        except ProtocolHandlerError:
            # Handle execution errors
            error_handled_by = "ProtocolHandlerError"
        except SPIError:
            # Catch-all for any other SPI error (pattern demonstration;
            # see test_spi_error_fallback_handler for actual exercise)
            error_handled_by = "SPIError"

        assert error_handled_by == "ProtocolHandlerError"

    @pytest.mark.asyncio
    async def test_exception_context_preserved_through_layers(self) -> None:
        """
        Exception context should be preserved through exception handling.

        Pattern: When catching and re-raising, preserve context for debugging.
        Context should travel up the call stack to error handlers.
        """
        handler = RealisticProtocolHandler(
            handler_id="context-test-handler",
            simulate_execute_failure=True,
        )
        config = MockConnectionConfig()
        await handler.initialize(config)

        request = MockProtocolRequest(operation="test-operation")
        op_config = MockOperationConfig()

        captured_context: dict[str, Any] = {}

        try:
            await handler.execute(request, op_config)
        except ProtocolHandlerError as e:
            captured_context = e.context

        # Verify all context is preserved
        assert captured_context["handler_id"] == "context-test-handler"
        assert captured_context["operation"] == "test-operation"
        assert captured_context["error_type"] == "service_unavailable"

    @pytest.mark.asyncio
    async def test_spi_error_fallback_handler(self) -> None:
        """
        SPIError catch-all handles errors not caught by specific handlers.

        Pattern: When using layered exception handling, the generic SPIError
        handler catches any SPI errors not matched by more specific handlers.
        This is the recommended pattern for robust error handling:

            try:
                operation()
            except SpecificError1:
                handle_specific_1()
            except SpecificError2:
                handle_specific_2()
            except SPIError:
                handle_any_other_spi_error()  # Fallback

        This test demonstrates that errors like RegistryError, which are
        NOT caught by InvalidProtocolStateError or ProtocolHandlerError,
        correctly fall through to the SPIError catch-all.
        """
        registry = RealisticHandlerRegistry()
        # Register one handler type
        registry.register("http", RealisticProtocolHandler)

        error_handled_by: str | None = None
        captured_error: SPIError | None = None

        # Attempt to look up an unregistered protocol type
        # This raises RegistryError, which is NOT caught by
        # InvalidProtocolStateError or ProtocolHandlerError
        try:
            registry.get("kafka")  # Not registered, will raise RegistryError
        except InvalidProtocolStateError:
            # This handler would catch state validation errors
            error_handled_by = "InvalidProtocolStateError"
        except ProtocolHandlerError:
            # This handler would catch execution errors
            error_handled_by = "ProtocolHandlerError"
        except SPIError as e:
            # Catch-all for any other SPI error (RegistryError falls here)
            error_handled_by = "SPIError"
            captured_error = e

        # Verify the fallback SPIError handler was reached
        assert error_handled_by == "SPIError", (
            f"Expected SPIError fallback, but got {error_handled_by}"
        )

        # Verify the captured error is actually a RegistryError
        assert captured_error is not None
        assert isinstance(captured_error, RegistryError)

        # Verify context is preserved even when caught as SPIError
        assert captured_error.context["protocol_type"] == "kafka"
        assert "http" in captured_error.context["available_types"]

    @pytest.mark.asyncio
    async def test_spi_error_fallback_with_contract_compiler_error(self) -> None:
        """
        SPIError fallback also catches ContractCompilerError.

        Pattern: This test reinforces that the SPIError catch-all works
        for multiple error types. ContractCompilerError represents a
        different domain (compilation) than RegistryError (registration),
        demonstrating the fallback's generality.
        """
        compiler = RealisticContractCompiler()

        error_handled_by: str | None = None
        captured_error: SPIError | None = None

        # Attempt to compile an empty contract
        # This raises ContractCompilerError
        try:
            compiler.compile("", path="empty.yaml")
        except InvalidProtocolStateError:
            error_handled_by = "InvalidProtocolStateError"
        except ProtocolHandlerError:
            error_handled_by = "ProtocolHandlerError"
        except SPIError as e:
            # ContractCompilerError falls through to SPIError
            error_handled_by = "SPIError"
            captured_error = e

        # Verify the fallback SPIError handler was reached
        assert error_handled_by == "SPIError"

        # Verify the captured error is actually a ContractCompilerError
        assert captured_error is not None
        assert isinstance(captured_error, ContractCompilerError)
        assert captured_error.context["error_type"] == "empty_file"


@pytest.mark.unit
class TestIdempotencyStoreExceptions:
    """
    Unit tests for idempotency store exception handling.

    These tests demonstrate proper exception usage in event deduplication
    scenarios.
    """

    def test_storage_failure_raises_idempotency_store_error(self) -> None:
        """
        Storage connection failure should raise IdempotencyStoreError.

        Pattern: Wrap storage errors with context about the operation
        that failed and the event being processed.
        """
        store = RealisticIdempotencyStore(simulate_failure=True)

        with pytest.raises(IdempotencyStoreError) as exc_info:
            store.record_event("evt-123", "key-456")

        assert exc_info.value.context["event_id"] == "evt-123"
        assert exc_info.value.context["idempotency_key"] == "key-456"
        assert exc_info.value.context["error_type"] == "connection_lost"

    def test_successful_event_recording(self) -> None:
        """
        Successful event recording should not raise exceptions.

        Pattern: Normal operation should complete without exceptions.
        """
        store = RealisticIdempotencyStore()

        # First recording succeeds
        result = store.record_event("evt-123", "key-456")
        assert result is True

        # Second recording returns False (duplicate)
        result = store.record_event("evt-124", "key-456")
        assert result is False


@pytest.mark.unit
class TestProjectorExceptions:
    """
    Unit tests for projector exception handling.

    These tests demonstrate proper exception usage in event sourcing
    projection scenarios.
    """

    @pytest.mark.asyncio
    async def test_projection_write_failure_raises_projector_error(self) -> None:
        """
        Projection persistence failure should raise ProjectorError.

        Pattern: Use ProjectorError for write failures. Include entity
        and domain information for debugging.
        """
        projector = RealisticProjector(simulate_write_failure=True)

        with pytest.raises(ProjectorError) as exc_info:
            await projector.persist(
                entity_id="order-123",
                domain="orders",
                state={"status": "pending"},
                sequence=1,
            )

        assert exc_info.value.context["entity_id"] == "order-123"
        assert exc_info.value.context["domain"] == "orders"
        assert exc_info.value.context["error_type"] == "write_failure"

    @pytest.mark.asyncio
    async def test_projection_read_failure_raises_projection_read_error(self) -> None:
        """
        Projection read failure should raise ProjectionReadError.

        Pattern: Use ProjectionReadError for read failures. This
        distinction helps separate read and write error handling.
        """
        projector = RealisticProjector(simulate_read_failure=True)

        with pytest.raises(ProjectionReadError) as exc_info:
            await projector.get_entity_state(
                entity_id="order-123",
                domain="orders",
            )

        assert exc_info.value.context["entity_id"] == "order-123"
        assert exc_info.value.context["operation"] == "get_entity_state"


@pytest.mark.unit
class TestContractCompilerExceptions:
    """
    Unit tests for contract compiler exception handling.

    These tests demonstrate proper exception usage during contract
    compilation and validation.
    """

    def test_empty_contract_raises_contract_compiler_error(self) -> None:
        """
        Empty contract file should raise ContractCompilerError.

        Pattern: Validate input early and provide specific error messages.
        """
        compiler = RealisticContractCompiler()

        with pytest.raises(ContractCompilerError) as exc_info:
            compiler.compile("", path="empty.yaml")

        assert exc_info.value.context["path"] == "empty.yaml"
        assert exc_info.value.context["error_type"] == "empty_file"

    def test_missing_required_fields_raises_contract_compiler_error(self) -> None:
        """
        Missing required fields should raise ContractCompilerError.

        Pattern: Identify all missing fields at once rather than
        failing on the first missing field.
        """
        compiler = RealisticContractCompiler()
        invalid_yaml = "name: test\ntype: effect"

        with pytest.raises(ContractCompilerError) as exc_info:
            compiler.compile(invalid_yaml, path="invalid.yaml")

        assert "protocol" in exc_info.value.context["missing_fields"]
        assert "version" in exc_info.value.context["missing_fields"]


@pytest.mark.unit
class TestExceptionRecoveryPatterns:
    """
    Unit tests demonstrating single-component exception recovery patterns.

    These tests show retry and logging patterns using a single component.
    For multi-component fallback patterns, see:
        tests/integration/test_exception_integration.py
    """

    @pytest.mark.asyncio
    async def test_retry_on_transient_failure(self) -> None:
        """
        Demonstrate retry pattern for transient failures.

        Pattern: Catch specific error types and implement retry logic.
        Use context to determine if retry is appropriate.
        """
        # Create handler that fails initially but succeeds after
        call_count = 0

        class RetryableHandler(RealisticProtocolHandler):
            """Handler that fails first call then succeeds."""

            async def execute(
                self,
                request: MockProtocolRequest,
                operation_config: MockOperationConfig,
            ) -> MockProtocolResponse:
                nonlocal call_count
                call_count += 1

                if self._state != "initialized":
                    raise InvalidProtocolStateError(
                        f"Cannot execute() in state '{self._state}'",
                        context={
                            "handler_id": self._handler_id,
                            "current_state": self._state,
                            "required_state": "initialized",
                            "operation": "execute",
                        },
                    )

                if call_count < 3:
                    raise ProtocolHandlerError(
                        "Transient failure",
                        context={
                            "handler_id": self._handler_id,
                            "error_type": "transient",
                            "retry_after_ms": 100,
                        },
                    )

                return MockProtocolResponse(status="success")

        handler = RetryableHandler()
        await handler.initialize(MockConnectionConfig())

        # Implement retry logic
        max_retries = 3
        result: MockProtocolResponse | None = None

        for attempt in range(max_retries):
            try:
                result = await handler.execute(
                    MockProtocolRequest(),
                    MockOperationConfig(),
                )
                break  # Success
            except ProtocolHandlerError as e:
                if (
                    e.context.get("error_type") == "transient"
                    and attempt < max_retries - 1
                ):
                    continue  # Retry
                raise

        assert result is not None
        assert result.status == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_error_logging_with_context(self) -> None:
        """
        Demonstrate how to log errors with full context.

        Pattern: Use exception context to construct detailed log messages
        that aid in debugging without exposing sensitive information.
        """
        handler = RealisticProtocolHandler(
            handler_id="logging-test",
            simulate_execute_failure=True,
        )
        await handler.initialize(MockConnectionConfig())

        logged_messages: list[str] = []

        try:
            await handler.execute(MockProtocolRequest(), MockOperationConfig())
        except ProtocolHandlerError as e:
            # Construct log message from context
            log_msg = (
                f"Handler {e.context.get('handler_id', 'unknown')} failed: {str(e)} "
                f"[operation={e.context.get('operation', 'unknown')}, "
                f"error_type={e.context.get('error_type', 'unknown')}]"
            )
            logged_messages.append(log_msg)

        assert len(logged_messages) == 1
        assert "logging-test" in logged_messages[0]
        assert "service_unavailable" in logged_messages[0]
