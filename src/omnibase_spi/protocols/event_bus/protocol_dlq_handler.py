"""
Dead Letter Queue Handler Protocol - ONEX SPI Interface

Protocol definition for DLQ monitoring and reprocessing.
Pure protocol interface following SPI zero-dependency principle.

Created: 2025-10-18
Reference: EVENT_BUS_ARCHITECTURE.md Phase 1
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolDLQHandler(Protocol):
    """
    Protocol for Dead Letter Queue monitoring and reprocessing.

    Defines contract for DLQ management:
    - DLQ message consumption and monitoring
    - Metrics tracking (message count, error patterns, age)
    - Reprocessing with backoff strategy
    - Alert integration for DLQ overflow

    Implementations must provide:
    - Kafka consumer for DLQ topics (*.dlq pattern)
    - Message parsing and error metadata extraction
    - Reprocessing capabilities
    - Alert threshold monitoring

    Example:
        ```python
        from omnibase_spi.protocols.event_bus import ProtocolDLQHandler

        # Get DLQ handler implementation
        handler: ProtocolDLQHandler = create_dlq_handler(
            bootstrap_servers="redpanda:9092",
            consumer_group="dlq-handler"
        )

        # Start monitoring
        await handler.start()

        # Get metrics
        metrics = await handler.get_metrics()
        print(f"Total DLQ messages: {metrics['total_dlq_messages']}")

        # Get summary
        summary = await handler.get_dlq_summary()
        print(f"Alert status: {summary['alert_status']}")

        # Reprocess messages
        results = await handler.reprocess_dlq(
            dlq_topic="omninode.codegen.request.validate.v1.dlq",
            limit=100
        )
        print(f"Reprocessed: {results['messages_reprocessed']}")

        # Stop handler
        await handler.stop()
        ```

    DLQ Message Structure:
        ```json
        {
          "original_topic": "omninode.codegen.request.validate.v1",
          "original_envelope": {...},
          "error_message": "Failed after max retries",
          "error_timestamp": 1697654400.0,
          "service": "archon-intelligence",
          "instance_id": "instance-123",
          "retry_count": 3
        }
        ```

    Alert Thresholds:
        - Total DLQ messages > alert_threshold (default: 100)
        - Oldest message age > max_dlq_message_age_hours (default: 24h)

    See Also:
        - ProtocolEventPublisher: Event publishing with DLQ routing
        - EVENT_BUS_ARCHITECTURE.md: DLQ strategy and runbooks
    """

    async def start(self) -> None:
        """
        Start DLQ handler.

        Initializes consumer and begins monitoring DLQ topics.
        Subscribes to all topics matching *.dlq pattern.

        Example:
            ```python
            await handler.start()
            print("DLQ handler started, monitoring all *.dlq topics")
            ```
        """
        ...

    async def stop(self, timeout_seconds: float = 30.0) -> None:
        """
        Stop DLQ handler gracefully.

        Stops consumer loop, commits offsets, and closes connections.

        Args:
            timeout_seconds: Maximum time to wait for shutdown to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If shutdown does not complete within the specified timeout.

        Example:
            ```python
            # Stop with default timeout
            await handler.stop()
            print("DLQ handler stopped")

            # Stop with custom timeout
            await handler.stop(timeout_seconds=60.0)
            ```
        """
        ...

    async def reprocess_dlq(
        self, dlq_topic: str, limit: int | None = None
    ) -> "JsonType":
        """
        Reprocess messages from specific DLQ topic.

        Republishes failed events to their original topics for reprocessing.

        Args:
            dlq_topic: DLQ topic to reprocess
            limit: Maximum messages to reprocess (None = all)

        Returns:
            Dict with reprocessing results:
            - messages_reprocessed: Count of messages successfully reprocessed
            - messages_failed: Count of messages that failed reprocessing
            - errors: List of errors encountered

        Example:
            ```python
            results = await handler.reprocess_dlq(
                dlq_topic="omninode.codegen.request.validate.v1.dlq",
                limit=100
            )

            print(f"Success: {results['messages_reprocessed']}")
            print(f"Failed: {results['messages_failed']}")
            if results['errors']:
                print(f"Errors: {results['errors']}")
            ```
        """
        ...

    async def get_metrics(self) -> "JsonType":
        """
        Get DLQ metrics.

        Returns:
            Dict with DLQ metrics:
            - total_dlq_messages: Total messages in DLQ
            - messages_by_topic: Breakdown by original topic
            - messages_by_error_type: Breakdown by error type
            - oldest_message_age_hours: Age of oldest message
            - reprocessing_success: Successful reprocessing count
            - reprocessing_failed: Failed reprocessing count
            - alerts_triggered: Number of alerts triggered

        Example:
            ```python
            metrics = await handler.get_metrics()

            print(f"Total DLQ messages: {metrics['total_dlq_messages']}")
            print(f"Oldest message: {metrics['oldest_message_age_hours']:.1f}h")
            print(f"Alerts triggered: {metrics['alerts_triggered']}")

            # Top failing topics
            for topic, count in metrics['messages_by_topic'].items():
                print(f"  {topic}: {count} messages")
            ```
        """
        ...

    async def get_dlq_summary(self) -> "JsonType":
        """
        Get summary of DLQ status.

        Returns:
            Dict with summary:
            - total_messages: Total DLQ messages
            - oldest_message_age_hours: Age of oldest message
            - top_failing_topics: Topics with most failures (top 5)
            - top_error_types: Most common error types (top 5)
            - alert_status: "OK" or "ALERT" based on thresholds
            - alerts_triggered: Number of alerts triggered

        Example:
            ```python
            summary = await handler.get_dlq_summary()

            print(f"Status: {summary['alert_status']}")
            print(f"Total messages: {summary['total_messages']}")
            print(f"Oldest message: {summary['oldest_message_age_hours']:.1f}h")

            print("Top failing topics:")
            for topic, count in summary['top_failing_topics'].items():
                print(f"  {topic}: {count}")

            print("Top error types:")
            for error_type, count in summary['top_error_types'].items():
                print(f"  {error_type}: {count}")
            ```
        """
        ...
