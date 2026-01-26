"""
Protocol definitions extracted from Event Bus Mixin.

Provides clean protocol interfaces for event bus operations without
implementation dependencies or mixin complexity.

This module supports two messaging patterns:

1. **Basic Event Messaging** (ProtocolEventMessage):
   - Simple event publishing with publish() method
   - Suitable for internal, non-serialized event passing
   - Used by sync/async bus variants

2. **Envelope-Based Messaging** (ModelEnvelope):
   - Structured envelope format with metadata, correlation IDs, and routing
   - Full serialization/deserialization support for Kafka transport
   - Consumer subscription model with handler callbacks
   - Health monitoring and lifecycle management
   - Used for cross-service communication and event sourcing
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import LiteralLogLevel
from omnibase_spi.protocols.types.protocol_event_bus_types import ProtocolEventMessage

if TYPE_CHECKING:
    # Forward reference to avoid circular import: ModelEnvelope is defined
    # in omnibase_core.models.common but used in type hints here.
    from omnibase_core.models.common import ModelEnvelope
    from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolEventBusBase(Protocol):
    """
    Base protocol for event bus operations.

    Defines common event publishing interface that both synchronous
    and asynchronous event buses must implement. Provides unified
    event publishing capabilities across different execution patterns.

    This protocol supports two messaging patterns:

    **Basic Event Messaging**:
        Use publish() for simple ProtocolEventMessage events. Suitable for
        internal event passing without full envelope serialization.

    **Envelope-Based Messaging**:
        Use publish_envelope(), subscribe(), and start_consuming() for
        structured ModelEnvelope messages. Provides:
        - Correlation ID tracking across service boundaries
        - Full metadata preservation (timestamps, routing keys)
        - Kafka-compatible serialization format
        - Consumer group subscription model

    Key Features:
        - Unified event publishing interface
        - Support for both sync and async implementations
        - Compatible with dependency injection patterns
        - Envelope support for cross-service messaging
        - Health monitoring for operational readiness
    """

    async def publish(self, event: ProtocolEventMessage) -> None:
        """
        Publish a basic event message.

        Args:
            event: The event message to publish.

        Raises:
            SPIError: If publishing fails.
        """
        ...

    async def publish_envelope(
        self,
        envelope: ModelEnvelope,
        topic: str,
    ) -> None:
        """
        Publish an envelope-wrapped event to a specific topic.

        Envelope-based publishing provides structured messaging with:
        - Correlation ID propagation for distributed tracing
        - Metadata preservation (timestamps, routing information)
        - Serialization-ready format for Kafka transport

        Args:
            envelope: The ONEX envelope containing the event payload
                and metadata (correlation_id, timestamp, etc.).
            topic: The Kafka topic or channel to publish to.

        Raises:
            SPIError: If publishing fails or topic is invalid.
        """
        ...

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[ModelEnvelope], Awaitable[None]],
    ) -> None:
        """
        Subscribe to a topic with an envelope handler.

        Registers an async handler function to process incoming envelopes
        from the specified topic. Multiple handlers can subscribe to the
        same topic.

        Args:
            topic: The Kafka topic or channel to subscribe to.
            handler: Async callback function that receives ModelEnvelope
                instances. Handler should process envelope.payload for
                the actual event data.

        Raises:
            SPIError: If subscription fails or topic is invalid.
        """
        ...

    async def start_consuming(self, timeout_seconds: float | None = None) -> None:
        """
        Start consuming messages from all subscribed topics.

        Activates the consumer loop to begin processing incoming envelopes.
        This method should be called after all subscribe() registrations
        are complete.

        Args:
            timeout_seconds: Maximum time to consume messages before returning.
                If None (default), runs indefinitely until stop() is called or
                the event bus is shut down. Useful for testing scenarios where
                bounded consumption is needed.

        Example:
            ```python
            # Run indefinitely (production usage)
            await bus.start_consuming()

            # Run for 30 seconds (testing usage)
            await bus.start_consuming(timeout_seconds=30.0)
            ```

        Raises:
            SPIError: If consumer initialization fails.
        """
        ...

    async def stop_consuming(self, timeout_seconds: float = 30.0) -> None:
        """
        Stop consuming messages and gracefully shut down the consumer.

        Signals the consumer loop to stop processing messages and cleanly
        exit. This method should be called to ensure proper resource cleanup
        and to allow in-flight messages to complete processing.

        This is the counterpart to start_consuming() and should be called
        during application shutdown or when consumption needs to be paused.

        Args:
            timeout_seconds: Maximum time to wait for graceful shutdown.
                Defaults to 30.0 seconds. After this timeout, the consumer
                will be forcefully terminated. Set to 0 for immediate
                termination (not recommended for production).

        Example:
            ```python
            # Graceful shutdown with default timeout
            await bus.stop_consuming()

            # Quick shutdown for testing
            await bus.stop_consuming(timeout_seconds=5.0)

            # Immediate termination (use with caution)
            await bus.stop_consuming(timeout_seconds=0)
            ```

        Raises:
            SPIError: If shutdown fails or times out unexpectedly.
        """
        ...

    async def health_check(self) -> JsonType:
        """
        Check the health status of the event bus connection.

        Verifies connectivity to the underlying message broker (e.g., Kafka)
        and returns operational readiness status with diagnostic details.

        Returns:
            Dictionary containing health status:
                - healthy: Boolean indicating overall health
                - latency_ms: Response time in milliseconds (optional)
                - details: Additional diagnostic information (optional)
                - last_error: Most recent error message if unhealthy (optional)

        Caching:
            Implementations SHOULD cache health check results for 5-30 seconds
            to avoid overwhelming the message broker with repeated health probes.
            Consider using a TTL cache for production deployments.

        Security:
            The `last_error` field may contain sensitive information from exception
            messages. Implementations SHOULD sanitize error messages by removing
            credentials, connection strings, and internal paths.

        Example:
            ```python
            health = await bus.health_check()
            if health['healthy']:
                print(f"Bus healthy, latency: {health.get('latency_ms', 'N/A')}ms")
            else:
                print(f"Bus unhealthy: {health.get('last_error', 'Unknown')}")
            ```

        Raises:
            SPIError: If health check cannot be performed.
        """
        ...


@runtime_checkable
class ProtocolSyncEventBus(ProtocolEventBusBase, Protocol):
    """
    Protocol for synchronous event bus operations.

    Defines synchronous event publishing interface for
    event bus implementations that operate synchronously.
    Inherits from ProtocolEventBusBase for unified interface.

    Key Features:
        - Synchronous event publishing
        - Basic publish interface
        - Compatible with sync event processing
    """

    async def publish_sync(self, event: ProtocolEventMessage) -> None:
        """Publish an event synchronously with blocking semantics.

        This method blocks until the event is confirmed delivered to the
        message broker, providing stronger delivery guarantees at the cost
        of latency.

        Args:
            event: The event message to publish synchronously.

        Raises:
            SPIError: If publishing fails or the event bus is not connected.
            TimeoutError: If the synchronous publish times out waiting for
                broker confirmation.
        """
        ...


@runtime_checkable
class ProtocolAsyncEventBus(ProtocolEventBusBase, Protocol):
    """
    Protocol for asynchronous event bus operations.

    Defines asynchronous event publishing interface for
    event bus implementations that operate asynchronously.
    Inherits from ProtocolEventBusBase for unified interface.

    Key Features:
        - Asynchronous event publishing
        - Async/await compatibility
        - Non-blocking event processing
    """

    async def publish_async(self, event: ProtocolEventMessage) -> None:
        """Publish an event asynchronously with non-blocking semantics.

        This method returns immediately after enqueueing the event for
        delivery, allowing the caller to continue processing without
        waiting for broker confirmation.

        Args:
            event: The event message to publish asynchronously.

        Raises:
            SPIError: If the event cannot be enqueued for delivery
                or the event bus is not connected.
        """
        ...


@runtime_checkable
class ProtocolEventBusRegistry(Protocol):
    """
    Protocol for registry that provides event bus access.

    Defines interface for service registries that provide
    access to event bus instances for dependency injection.

    Key Features:
        - Event bus dependency injection
        - Registry-based service location
        - Support for both sync and async event buses
    """

    event_bus: ProtocolEventBusBase | None

    async def validate_registry_bus(self) -> bool:
        """Validate that the registry's event bus is operational.

        Performs a health check on the registered event bus to verify
        connectivity and operational readiness.

        Returns:
            True if the event bus is valid and operational, False otherwise.

        Raises:
            SPIError: If validation fails due to an unexpected error.
        """
        ...

    def has_bus_access(self) -> bool:
        """Check if the registry has an event bus instance available.

        Returns:
            True if an event bus instance is registered and accessible,
            False if no event bus is configured.
        """
        ...


@runtime_checkable
class ProtocolEventBusLogEmitter(Protocol):
    """
    Protocol for structured log emission.

    Defines interface for components that can emit structured
    log events with typed data and log levels.

    Key Features:
        - Structured logging support
        - Log level management
        - Typed log data
    """

    def emit_log_event(
        self,
        level: LiteralLogLevel,
        message: str,
        data: dict[str, str | int | float | bool],
    ) -> None:
        """Emit a structured log event with typed data.

        Emits a log event to the event bus or logging infrastructure with
        structured data that can be queried and analyzed.

        Args:
            level: The log level for this event (e.g., "DEBUG", "INFO",
                "WARNING", "ERROR", "CRITICAL").
            message: Human-readable log message describing the event.
            data: Structured data associated with the log event. Keys should
                be descriptive identifiers, values must be primitive types
                (str, int, float, bool) for serialization compatibility.

        Example:
            ```python
            emitter.emit_log_event(
                level="INFO",
                message="Order processed successfully",
                data={
                    "order_id": "order-123",
                    "processing_time_ms": 45,
                    "item_count": 3,
                    "success": True,
                }
            )
            ```
        """
        ...
