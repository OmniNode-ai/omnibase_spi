"""
Shared test fixtures and mock implementations for omnibase_spi tests.

This module provides shared mock implementations that are used across both
unit and integration tests. Pytest automatically discovers fixtures from
conftest.py files.

Mock Classes:
    MockConnectionConfig: Mock connection configuration
    MockProtocolRequest: Mock protocol request
    MockOperationConfig: Mock operation configuration
    MockProtocolResponse: Mock protocol response
    RealisticProtocolHandler: Full-featured mock handler with lifecycle support
    RealisticHandlerRegistry: Mock registry with registration/lookup support
    RealisticIdempotencyStore: Mock idempotency store for event deduplication
    RealisticProjector: Mock projector for event sourcing patterns

For event bus mocks, see tests/integration/conftest.py.
"""

from __future__ import annotations

from typing import Any

from omnibase_core.enums import (
    EnumHandlerRole,
    EnumHandlerType,
    EnumHandlerTypeCategory,
)
from omnibase_core.models.handlers import ModelHandlerDescriptor, ModelIdentifier
from omnibase_core.models.primitives.model_semver import ModelSemVer
from omnibase_spi.exceptions import (
    HandlerInitializationError,
    IdempotencyStoreError,
    InvalidProtocolStateError,
    ProjectionReadError,
    ProjectorError,
    ProtocolHandlerError,
    ProtocolNotImplementedError,
    RegistryError,
)

# =============================================================================
# Mock Data Classes
# =============================================================================


class MockConnectionConfig:
    """
    Mock connection configuration for testing protocol handlers.

    Simulates connection settings used when initializing protocol handlers.

    Attributes:
        url: Connection URL (e.g., "http://localhost:8080")
        timeout: Connection timeout in seconds
        valid: Whether this configuration is valid (for testing validation)

    Example:
        config = MockConnectionConfig(url="http://api.example.com", timeout=30.0)
        await handler.initialize(config)
    """

    def __init__(
        self,
        url: str = "http://localhost:8080",
        timeout: float = 30.0,
        valid: bool = True,
    ) -> None:
        """
        Initialize mock connection configuration.

        Args:
            url: Connection URL.
            timeout: Connection timeout in seconds.
            valid: Whether this configuration is considered valid.
        """
        self.url = url
        self.timeout = timeout
        self.valid = valid


class MockProtocolRequest:
    """
    Mock protocol request for testing handler execution.

    Simulates a request object passed to protocol handlers.

    Attributes:
        operation: Operation type (e.g., "query", "mutate")
        payload: Request payload data

    Example:
        request = MockProtocolRequest(operation="query", payload={"id": 123})
        response = await handler.execute(request, op_config)
    """

    def __init__(
        self,
        operation: str = "query",
        payload: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize mock protocol request.

        Args:
            operation: Operation type identifier.
            payload: Optional request payload.
        """
        self.operation = operation
        self.payload = payload or {}


class MockOperationConfig:
    """
    Mock operation configuration for testing handler execution.

    Simulates per-operation settings for protocol handlers.

    Attributes:
        timeout: Operation timeout in seconds
        retries: Number of retry attempts

    Example:
        op_config = MockOperationConfig(timeout=5.0, retries=3)
        response = await handler.execute(request, op_config)
    """

    def __init__(
        self,
        timeout: float = 5.0,
        retries: int = 3,
    ) -> None:
        """
        Initialize mock operation configuration.

        Args:
            timeout: Operation timeout in seconds.
            retries: Number of retry attempts.
        """
        self.timeout = timeout
        self.retries = retries


class MockProtocolResponse:
    """
    Mock protocol response for testing handler execution.

    Simulates a response object returned from protocol handlers.

    Attributes:
        status: Response status (e.g., "success", "error")
        data: Response data

    Example:
        response = await handler.execute(request, op_config)
        assert response.status == "success"
    """

    def __init__(
        self,
        status: str = "success",
        data: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize mock protocol response.

        Args:
            status: Response status.
            data: Optional response data.
        """
        self.status = status
        self.data = data or {}


# =============================================================================
# Mock Protocol Implementations
# =============================================================================


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

    Example:
        handler = RealisticProtocolHandler(handler_id="my-handler")
        await handler.initialize(MockConnectionConfig())
        response = await handler.execute(MockProtocolRequest(), MockOperationConfig())
        await handler.shutdown()
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
            InvalidProtocolStateError: If handler already shutdown.
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

    def describe(self) -> ModelHandlerDescriptor:
        """Return handler metadata."""
        return ModelHandlerDescriptor(
            handler_name=ModelIdentifier(
                namespace="test",
                name=self._handler_id,
            ),
            handler_version=ModelSemVer(major=1, minor=0, patch=0),
            handler_role=EnumHandlerRole.INFRA_HANDLER,
            handler_type=EnumHandlerType.NAMED,
            handler_type_category=EnumHandlerTypeCategory.EFFECT,
        )

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
        - ProtocolNotImplementedError: When a required protocol has no implementation

    Example:
        registry = RealisticHandlerRegistry()
        registry.register("http", HttpHandler)
        handler_class = registry.get("http")
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

    def get_or_raise_not_implemented(self, key: str) -> type[object]:
        """
        Get handler or raise ProtocolNotImplementedError.

        This method demonstrates the difference between RegistryError
        (lookup failure) and ProtocolNotImplementedError (missing implementation).

        Use ProtocolNotImplementedError when the absence of an implementation
        represents a missing feature rather than a configuration error.

        Args:
            key: Protocol type identifier.

        Returns:
            Handler class for the protocol type.

        Raises:
            ProtocolNotImplementedError: If no implementation registered.
        """
        if key not in self._handlers:
            raise ProtocolNotImplementedError(
                f"No implementation registered for protocol '{key}'",
                context={
                    "protocol_name": key,
                    "available_implementations": list(self._handlers.keys()),
                    "required_by": "get_or_raise_not_implemented",
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

    Exception Usage:
        - IdempotencyStoreError: Connection failures, write failures

    Example:
        store = RealisticIdempotencyStore()
        if store.record_event("evt-123", "order:created:123"):
            # First occurrence - process event
            pass
        else:
            # Duplicate - skip processing
            pass
    """

    def __init__(self, simulate_failure: bool = False) -> None:
        """
        Initialize the store.

        Args:
            simulate_failure: If True, operations will raise IdempotencyStoreError.
        """
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

        Raises:
            IdempotencyStoreError: If storage operation fails.
        """
        if self._simulate_failure:
            raise IdempotencyStoreError(
                "Failed to record event: Storage connection lost",
                context={
                    "event_id": event_id,
                    "idempotency_key": idempotency_key,
                    "operation": "record",
                    "store_type": "mock",
                    "error_type": "connection_lost",
                },
            )

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
    for projection-related failures in event sourcing patterns.

    Exception Usage:
        - ProjectorError: Write/persistence failures
        - ProjectionReadError: Read/query failures

    Example:
        projector = RealisticProjector()
        await projector.persist("order-123", "orders", {"status": "pending"}, 1)
        state = await projector.get_entity_state("order-123", "orders")
    """

    def __init__(
        self,
        simulate_write_failure: bool = False,
        simulate_read_failure: bool = False,
    ) -> None:
        """
        Initialize the projector.

        Args:
            simulate_write_failure: If True, persist() will raise ProjectorError.
            simulate_read_failure: If True, get_entity_state() will raise
                ProjectionReadError.
        """
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

        Raises:
            ProjectorError: If persistence fails.
        """
        if self._simulate_write_failure:
            raise ProjectorError(
                f"Failed to persist projection for entity: {entity_id}",
                context={
                    "entity_id": entity_id,
                    "domain": domain,
                    "sequence": sequence,
                    "operation": "persist",
                    "store_type": "mock",
                    "error_type": "write_failure",
                },
            )

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

        Raises:
            ProjectionReadError: If read operation fails.
        """
        if self._simulate_read_failure:
            raise ProjectionReadError(
                f"Failed to query projection for entity: {entity_id}",
                context={
                    "entity_id": entity_id,
                    "domain": domain,
                    "operation": "get_entity_state",
                    "error_type": "read_timeout",
                },
            )

        key = f"{domain}:{entity_id}"
        if key in self._projections:
            state: dict[str, Any] = self._projections[key]["state"]
            return state
        return None
