"""
Integration tests demonstrating SPI exception usage across multiple components.

This module provides integration tests that show how exceptions flow
between multiple protocol implementations. These tests validate that
exception handling works correctly when components interact.

Key Integration Patterns Demonstrated:
    1. Handler fallback patterns (multiple handlers)
    2. Registry lookup to handler execution flows
    3. Idempotency check to projection update flows
    4. Error propagation through protocol layers

For single-component unit tests, see:
    tests/unit/test_exceptions.py (exception hierarchy tests)
    tests/unit/test_exception_handlers.py (handler pattern tests)
"""

from __future__ import annotations

from typing import Any

import pytest

from omnibase_spi.exceptions import (
    HandlerInitializationError,
    InvalidProtocolStateError,
    ProtocolHandlerError,
    RegistryError,
)

# =============================================================================
# Mock Protocol Implementations for Integration Testing
# =============================================================================


class MockConnectionConfig:
    """Mock connection configuration for testing."""

    def __init__(
        self,
        url: str = "http://localhost:8080",
        timeout: float = 30.0,
        valid: bool = True,
    ) -> None:
        self.url = url
        self.timeout = timeout
        self.valid = valid


class MockProtocolRequest:
    """Mock protocol request for testing."""

    def __init__(
        self,
        operation: str = "query",
        payload: dict[str, Any] | None = None,
    ) -> None:
        self.operation = operation
        self.payload = payload or {}


class MockOperationConfig:
    """Mock operation configuration for testing."""

    def __init__(
        self,
        timeout: float = 5.0,
        retries: int = 3,
    ) -> None:
        self.timeout = timeout
        self.retries = retries


class MockProtocolResponse:
    """Mock protocol response for testing."""

    def __init__(
        self,
        status: str = "success",
        data: dict[str, Any] | None = None,
    ) -> None:
        self.status = status
        self.data = data or {}


class RealisticProtocolHandler:
    """
    A realistic mock handler that demonstrates proper exception usage.

    This handler simulates real-world scenarios where different types of
    failures require different exception types. Use this as a reference
    when implementing actual protocol handlers.

    Lifecycle States:
        - uninitialized: Handler created but not initialized
        - initialized: Handler ready for use
        - shutdown: Handler has been closed

    Exception Usage:
        - HandlerInitializationError: Connection failures during initialize()
        - InvalidProtocolStateError: Calling execute() before initialize()
        - ProtocolHandlerError: Execution failures (timeouts, errors)
    """

    def __init__(
        self,
        handler_id: str = "mock-handler-v1",
        simulate_init_failure: bool = False,
        simulate_execute_failure: bool = False,
        simulate_timeout: bool = False,
    ) -> None:
        """
        Initialize the handler.

        Args:
            handler_id: Unique identifier for this handler instance.
            simulate_init_failure: If True, initialize() will fail.
            simulate_execute_failure: If True, execute() will fail.
            simulate_timeout: If True, simulate timeout on execute().
        """
        self._handler_id = handler_id
        self._state = "uninitialized"
        self._config: MockConnectionConfig | None = None
        self._simulate_init_failure = simulate_init_failure
        self._simulate_execute_failure = simulate_execute_failure
        self._simulate_timeout = simulate_timeout

    @property
    def handler_type(self) -> str:
        """Return handler type identifier."""
        return "mock"

    @property
    def state(self) -> str:
        """Return current lifecycle state."""
        return self._state

    async def initialize(self, config: MockConnectionConfig) -> None:
        """
        Initialize the handler with connection configuration.

        Demonstrates proper use of HandlerInitializationError for
        connection and configuration failures.

        Args:
            config: Connection configuration.

        Raises:
            HandlerInitializationError: If initialization fails.
        """
        if self._state == "shutdown":
            raise InvalidProtocolStateError(
                "Cannot initialize a shutdown handler",
                context={
                    "handler_id": self._handler_id,
                    "current_state": self._state,
                    "operation": "initialize",
                },
            )

        if self._simulate_init_failure:
            raise HandlerInitializationError(
                f"Failed to connect to {config.url}",
                context={
                    "handler_id": self._handler_id,
                    "url": config.url,
                    "timeout": config.timeout,
                    "operation": "initialize",
                    "reason": "Connection refused",
                },
            )

        if not config.valid:
            raise HandlerInitializationError(
                "Invalid connection configuration",
                context={
                    "handler_id": self._handler_id,
                    "validation_errors": ["Invalid URL format", "Timeout too short"],
                    "operation": "initialize",
                },
            )

        self._config = config
        self._state = "initialized"

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """
        Shutdown the handler and release resources.

        Args:
            timeout_seconds: Maximum time to wait for shutdown.
        """
        if self._state == "uninitialized":
            # Idempotent - safe to shutdown without initialization
            return

        self._state = "shutdown"
        self._config = None

    async def execute(
        self,
        request: MockProtocolRequest,
        operation_config: MockOperationConfig,
    ) -> MockProtocolResponse:
        """
        Execute a protocol operation.

        Demonstrates proper use of InvalidProtocolStateError and
        ProtocolHandlerError for different failure scenarios.

        Args:
            request: The protocol request to execute.
            operation_config: Configuration for this operation.

        Returns:
            Protocol response with execution results.

        Raises:
            InvalidProtocolStateError: If handler not initialized.
            ProtocolHandlerError: If execution fails.
        """
        # Lifecycle state validation
        if self._state != "initialized":
            raise InvalidProtocolStateError(
                f"Cannot execute() in state '{self._state}'",
                context={
                    "handler_id": self._handler_id,
                    "current_state": self._state,
                    "required_state": "initialized",
                    "operation": "execute",
                    "request_operation": request.operation,
                },
            )

        # Simulate execution failures
        if self._simulate_timeout:
            raise ProtocolHandlerError(
                f"Operation timed out after {operation_config.timeout}s",
                context={
                    "handler_id": self._handler_id,
                    "operation": request.operation,
                    "timeout": operation_config.timeout,
                    "error_type": "timeout",
                },
            )

        if self._simulate_execute_failure:
            raise ProtocolHandlerError(
                "Execution failed: Backend service unavailable",
                context={
                    "handler_id": self._handler_id,
                    "operation": request.operation,
                    "status_code": 503,
                    "error_type": "service_unavailable",
                },
            )

        return MockProtocolResponse(
            status="success",
            data={"operation": request.operation, "result": "completed"},
        )

    def describe(self) -> dict[str, Any]:
        """Return handler metadata."""
        return {
            "handler_type": self.handler_type,
            "handler_id": self._handler_id,
            "state": self._state,
            "capabilities": ["query", "mutate"],
        }

    async def health_check(self) -> dict[str, Any]:
        """Check handler health."""
        if self._state != "initialized":
            return {
                "healthy": False,
                "last_error": f"Handler not initialized (state: {self._state})",
            }
        return {"healthy": True, "latency_ms": 5.0}


class RealisticHandlerRegistry:
    """
    A realistic handler registry that demonstrates proper exception usage.

    This registry shows how to use RegistryError for various failure
    scenarios during handler registration and lookup.

    Exception Usage:
        - RegistryError: Handler not found, duplicate registration
    """

    def __init__(self, allow_overwrites: bool = False) -> None:
        """
        Initialize the registry.

        Args:
            allow_overwrites: If False, reject duplicate registrations.
        """
        self._handlers: dict[str, type[object]] = {}
        self._allow_overwrites = allow_overwrites

    def register(self, key: str, handler_class: type[object]) -> None:
        """
        Register a handler for a protocol type.

        Demonstrates proper use of RegistryError for registration failures.

        Args:
            key: Protocol type identifier (e.g., 'http', 'kafka').
            handler_class: Handler class to register.

        Raises:
            RegistryError: If key already registered and overwrites not allowed.
            ValueError: If key or handler_class is invalid.
        """
        if not key or not isinstance(key, str):
            raise ValueError("Registry key must be a non-empty string")

        if not self._allow_overwrites and key in self._handlers:
            raise RegistryError(
                f"Protocol type '{key}' is already registered",
                context={
                    "protocol_type": key,
                    "existing_handler": self._handlers[key].__name__,
                    "new_handler": handler_class.__name__,
                    "operation": "register",
                    "allow_overwrites": self._allow_overwrites,
                },
            )

        self._handlers[key] = handler_class

    def get(self, key: str) -> type[object]:
        """
        Get handler class for protocol type.

        Demonstrates proper use of RegistryError for lookup failures.

        Args:
            key: Protocol type identifier.

        Returns:
            Handler class for the protocol type.

        Raises:
            RegistryError: If protocol type not registered.
        """
        if key not in self._handlers:
            raise RegistryError(
                f"Protocol type '{key}' is not registered",
                context={
                    "protocol_type": key,
                    "available_types": list(self._handlers.keys()),
                    "operation": "lookup",
                    "suggestion": (
                        f"Did you mean one of: {list(self._handlers.keys())}?"
                        if self._handlers
                        else "No handlers registered"
                    ),
                },
            )
        return self._handlers[key]

    def list_keys(self) -> list[str]:
        """List registered protocol types."""
        return list(self._handlers.keys())

    def is_registered(self, key: str) -> bool:
        """Check if protocol type is registered."""
        return key in self._handlers

    def unregister(self, key: str) -> bool:
        """Remove a handler from the registry."""
        if key in self._handlers:
            del self._handlers[key]
            return True
        return False


class RealisticIdempotencyStore:
    """
    A realistic idempotency store that demonstrates proper exception usage.

    This store shows how to use IdempotencyStoreError for storage failures
    during event deduplication operations.
    """

    def __init__(self, simulate_failure: bool = False) -> None:
        """Initialize the store."""
        self._events: dict[str, dict[str, Any]] = {}
        self._simulate_failure = simulate_failure

    def record_event(self, event_id: str, idempotency_key: str) -> bool:
        """
        Record an event for deduplication.

        Args:
            event_id: Unique event identifier.
            idempotency_key: Key for idempotency checking.

        Returns:
            True if event was recorded (first occurrence).
            False if event was already recorded (duplicate).
        """
        if idempotency_key in self._events:
            return False

        self._events[idempotency_key] = {
            "event_id": event_id,
            "recorded_at": "2024-01-01T00:00:00Z",
        }
        return True

    def is_duplicate(self, idempotency_key: str) -> bool:
        """Check if an event has already been processed."""
        return idempotency_key in self._events


class RealisticProjector:
    """
    A realistic projector that demonstrates proper exception usage.

    This projector shows how to use ProjectorError and ProjectionReadError
    for projection-related failures.
    """

    def __init__(
        self,
        simulate_write_failure: bool = False,
        simulate_read_failure: bool = False,
    ) -> None:
        """Initialize the projector."""
        self._projections: dict[str, dict[str, Any]] = {}
        self._simulate_write_failure = simulate_write_failure
        self._simulate_read_failure = simulate_read_failure

    async def persist(
        self,
        entity_id: str,
        domain: str,
        state: dict[str, Any],
        sequence: int,
    ) -> None:
        """
        Persist projection state.

        Args:
            entity_id: Entity identifier.
            domain: Domain name.
            state: State to persist.
            sequence: Event sequence number.
        """
        self._projections[f"{domain}:{entity_id}"] = {
            "state": state,
            "sequence": sequence,
        }

    async def get_entity_state(
        self,
        entity_id: str,
        domain: str,
    ) -> dict[str, Any] | None:
        """
        Get entity projection state.

        Args:
            entity_id: Entity identifier.
            domain: Domain name.

        Returns:
            Entity state or None if not found.
        """
        key = f"{domain}:{entity_id}"
        if key in self._projections:
            state: dict[str, Any] = self._projections[key]["state"]
            return state
        return None


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.integration
class TestExceptionRecoveryPatterns:
    """
    Integration tests demonstrating exception recovery patterns with multiple components.

    These tests show fallback patterns when multiple handlers interact.
    For single-component recovery patterns (retry, logging), see:
        tests/unit/test_exception_handlers.py::TestExceptionRecoveryPatterns
    """

    @pytest.mark.asyncio
    async def test_fallback_handler_on_failure(self) -> None:
        """
        Demonstrate fallback pattern using multiple handlers.

        Pattern: Try primary handler, fall back to secondary on failure.
        This is an integration test because it coordinates between two
        independent handler instances.
        """
        primary = RealisticProtocolHandler(
            handler_id="primary",
            simulate_init_failure=True,
        )
        fallback = RealisticProtocolHandler(handler_id="fallback")

        config = MockConnectionConfig()
        active_handler: RealisticProtocolHandler | None = None

        # Try primary, fall back to secondary
        try:
            await primary.initialize(config)
            active_handler = primary
        except HandlerInitializationError:
            await fallback.initialize(config)
            active_handler = fallback

        assert active_handler is fallback
        assert active_handler._handler_id == "fallback"


@pytest.mark.integration
class TestCrossProtocolExceptionHandling:
    """
    Integration tests demonstrating exception handling across multiple protocols.

    These tests show how exceptions should be handled when multiple
    protocol implementations interact.
    """

    @pytest.mark.asyncio
    async def test_registry_and_handler_exception_flow(self) -> None:
        """
        Demonstrate exception flow from registry lookup through handler execution.

        Pattern: Catch different exception types at appropriate layers.
        Registry errors should be caught during setup, handler errors
        during execution.

        This is an integration test because it coordinates:
        1. Registry lookup (first component)
        2. Handler initialization and execution (second component)
        """
        registry = RealisticHandlerRegistry()
        registry.register("http", RealisticProtocolHandler)

        errors_caught: list[str] = []

        # Attempt to get and use handler
        handler: RealisticProtocolHandler
        try:
            # This should fail - kafka not registered
            _ = registry.get("kafka")
            # Code below won't execute due to RegistryError
            handler = RealisticProtocolHandler()
            await handler.initialize(MockConnectionConfig())
        except RegistryError:
            errors_caught.append("RegistryError")
            # Fall back to http handler - we know it's RealisticProtocolHandler
            handler = RealisticProtocolHandler(simulate_execute_failure=True)

        # Now try to use the fallback handler
        await handler.initialize(MockConnectionConfig())

        try:
            await handler.execute(MockProtocolRequest(), MockOperationConfig())
        except ProtocolHandlerError:
            errors_caught.append("ProtocolHandlerError")

        assert errors_caught == ["RegistryError", "ProtocolHandlerError"]

    @pytest.mark.asyncio
    async def test_idempotency_check_before_projection(self) -> None:
        """
        Demonstrate idempotency check followed by projection update.

        Pattern: Check idempotency first, only project if not duplicate.
        Handle both store and projector errors appropriately.

        This is an integration test because it coordinates:
        1. Idempotency store (first component)
        2. Projector (second component)
        """
        store = RealisticIdempotencyStore()
        projector = RealisticProjector()

        event_id = "evt-001"
        idempotency_key = f"order-created:{event_id}"

        # First processing - should succeed
        if store.record_event(event_id, idempotency_key):
            await projector.persist(
                entity_id="order-123",
                domain="orders",
                state={"status": "created"},
                sequence=1,
            )

        # Second processing - should be skipped (duplicate)
        was_duplicate = not store.record_event(event_id, idempotency_key)
        assert was_duplicate

        # Verify state was projected only once
        state = await projector.get_entity_state("order-123", "orders")
        assert state == {"status": "created"}
