"""
Event Publisher Protocol - ONEX SPI Interface

Protocol definition for event publishers with retry, circuit breaker, and validation.
Pure protocol interface following SPI zero-dependency principle.

Created: 2025-10-18
Reference: EVENT_BUS_ARCHITECTURE.md Phase 1
"""

from typing import Any, Protocol, runtime_checkable

if __name__ != "__main__":
    # Avoid circular imports in runtime
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolEventPublisher(Protocol):
    """
    Protocol for event publishers with reliability features.

    Defines contract for publishing events with:
    - Retry logic with exponential backoff
    - Circuit breaker to prevent cascading failures
    - Event validation before publishing
    - Correlation ID tracking
    - Dead letter queue (DLQ) routing
    - Metrics tracking

    Implementations must provide:
    - Kafka/Redpanda event publishing
    - Automatic retries with configurable backoff
    - Circuit breaker state management
    - DLQ routing on persistent failures
    - Performance metrics

    Example:
        ```python
        from omnibase_spi.protocols.event_bus import ProtocolEventPublisher

        # Get publisher implementation
        publisher: ProtocolEventPublisher = create_event_publisher(
            bootstrap_servers="redpanda:9092",
            service_name="my-service",
            instance_id="instance-123"
        )

        # Publish event
        success = await publisher.publish(
            event_type="omninode.my_domain.event.something_happened.v1",
            payload={"key": "value"},
            correlation_id="correlation-123"
        )

        # Get metrics
        metrics = publisher.get_metrics()
        print(f"Published: {metrics['events_published']}")

        # Clean shutdown
        await publisher.close()
        ```

    Circuit Breaker:
        Opens after threshold failures, preventing additional publish attempts.
        Automatically resets after timeout period or successful publish.

    Dead Letter Queue:
        Failed events (after max retries) are routed to DLQ topics with error metadata.
        Topic naming: {original_topic}.dlq

    See Also:
        - ProtocolDLQHandler: DLQ monitoring and reprocessing
        - ProtocolSchemaRegistry: Schema validation
        - EVENT_BUS_ARCHITECTURE.md: Complete event bus specification
    """

    async def publish(
        self,
        event_type: str,
        payload: Any,
        correlation_id: str | None = None,
        causation_id: str | None = None,
        metadata: dict[str, "ContextValue"] | None = None,
        topic: str | None = None,
        partition_key: str | None = None,
    ) -> bool:
        """
        Publish event to Kafka with retry and circuit breaker.

        Args:
            event_type: Fully-qualified event type (e.g., "omninode.codegen.request.validate.v1")
            payload: Event payload (dict or Pydantic model)
            correlation_id: Optional correlation ID (generated if not provided)
            causation_id: Optional causation ID for event sourcing
            metadata: Optional event metadata
            topic: Optional topic override (defaults to event_type)
            partition_key: Optional partition key for ordering

        Returns:
            True if published successfully, False otherwise

        Raises:
            RuntimeError: If circuit breaker is open

        Example:
            ```python
            success = await publisher.publish(
                event_type="omninode.intelligence.event.quality_assessed.v1",
                payload={
                    "entity_id": "file.py",
                    "quality_score": 0.87,
                    "onex_compliance": 0.92
                },
                correlation_id="request-123"
            )

            if success:
                print("Event published successfully")
            else:
                print("Event publish failed, sent to DLQ")
            ```
        """
        ...

    async def get_metrics(self) -> dict[str, Any]:
        """
        Get publisher metrics.

        Returns:
            Dictionary with metrics:
            - events_published: Total events published successfully
            - events_failed: Total events that failed publishing
            - events_sent_to_dlq: Total events sent to DLQ
            - total_publish_time_ms: Cumulative publish time
            - avg_publish_time_ms: Average publish time per event
            - circuit_breaker_opens: Times circuit breaker opened
            - retries_attempted: Total retry attempts
            - circuit_breaker_status: Current circuit breaker status
            - current_failures: Current failure count

        Example:
            ```python
            metrics = await publisher.get_metrics()

            print(f"Published: {metrics['events_published']}")
            print(f"Failed: {metrics['events_failed']}")
            print(f"Avg latency: {metrics['avg_publish_time_ms']:.2f}ms")
            print(f"Circuit breaker: {metrics['circuit_breaker_status']}")
            ```
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """
        Close publisher and flush pending messages.

        Ensures all pending messages are delivered before shutdown.
        Should be called during graceful shutdown to prevent message loss.

        Args:
            timeout_seconds: Maximum time to wait for cleanup to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If cleanup does not complete within the specified timeout.

        Example:
            ```python
            # Graceful shutdown with default timeout
            await publisher.close()
            print("Publisher closed, all messages flushed")

            # Graceful shutdown with custom timeout
            await publisher.close(timeout_seconds=60.0)
            ```
        """
        ...
