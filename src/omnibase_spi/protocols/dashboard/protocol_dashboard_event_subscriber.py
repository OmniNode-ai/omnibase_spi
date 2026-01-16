"""Dashboard Event Subscriber Protocol - ONEX SPI Interface.

This module provides the protocol definition for dashboard event subscription
in the ONEX platform. It defines the contract for subscribing to real-time
event streams to enable live dashboard updates and notifications.

The event subscriber enables dashboards to receive real-time updates about:
    - Node execution status changes
    - Workflow progress and completion
    - Metric updates and threshold alerts
    - System health and performance events

Key Protocol:
    - ProtocolDashboardEventSubscriber: Subscribe to event topics for real-time updates.

Ticket Reference: OMN-1285

Example:
    ```python
    from omnibase_spi.protocols.dashboard import ProtocolDashboardEventSubscriber

    # Get subscriber from dependency injection
    subscriber: ProtocolDashboardEventSubscriber = get_dashboard_subscriber()

    # Define callback for handling events
    def handle_event(topic: str, event_data: dict[str, Any]) -> None:
        print(f"Received event on {topic}: {event_data}")

    # Subscribe to multiple topics
    await subscriber.subscribe(
        topics=["node.execution.completed", "workflow.status.changed"],
        callback=handle_event
    )

    # Check subscription status
    if subscriber.is_subscribed:
        print(f"Subscribed to: {subscriber.subscribed_topics}")

    # Cleanup when done
    await subscriber.unsubscribe()
    ```

See Also:
    - ProtocolDashboardService: Dashboard lifecycle management.
    - ProtocolRegistryQueryService: Read-only registry queries for dashboard display.
    - ProtocolWidgetRenderer: Widget rendering for dashboard components.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Protocol, runtime_checkable

# Type alias for event callback function signature
DashboardEventCallback = Callable[[str, dict[str, Any]], None]
"""Callback type for dashboard event handlers.

Args:
    topic: The topic name the event was received on.
    event_data: The event payload as a dictionary.
"""


@runtime_checkable
class ProtocolDashboardEventSubscriber(Protocol):
    """
    Protocol for subscribing to real-time dashboard event streams.

    Enables dashboards to receive live updates by subscribing to event topics
    published by the ONEX event bus. Supports multiple topic subscriptions
    with a single callback handler.

    This protocol is designed for:
        - Real-time dashboard updates without polling
        - Live node execution status monitoring
        - Workflow progress tracking
        - System health alerts and notifications

    Example:
        ```python
        subscriber: ProtocolDashboardEventSubscriber = get_subscriber()

        # Track subscription state
        print(f"Currently subscribed: {subscriber.is_subscribed}")
        print(f"Active topics: {subscriber.subscribed_topics}")

        # Subscribe to node execution events
        def on_node_event(topic: str, data: dict[str, Any]) -> None:
            node_id = data.get("node_id")
            status = data.get("status")
            print(f"Node {node_id} is now {status}")

        await subscriber.subscribe(
            topics=["node.execution.started", "node.execution.completed"],
            callback=on_node_event
        )

        # Later, unsubscribe to stop receiving events
        await subscriber.unsubscribe()
        ```

    Thread Safety:
        Implementations should be thread-safe to allow subscription
        management from different contexts while events are being
        delivered to the callback.

    See Also:
        - ProtocolDashboardService: For dashboard lifecycle management.
        - ProtocolRegistryQueryService: For read-only registry queries.
        - ProtocolKafkaAdapter: Underlying event bus adapter.
    """

    @property
    def is_subscribed(self) -> bool:
        """
        Whether the subscriber currently has active subscriptions.

        Returns:
            True if subscribed to at least one topic, False otherwise.

        Example:
            ```python
            if not subscriber.is_subscribed:
                await subscriber.subscribe(topics, callback)
            ```
        """
        ...

    @property
    def subscribed_topics(self) -> Sequence[str]:
        """
        Get the list of currently subscribed topics.

        Returns:
            Sequence of topic names currently subscribed to.
            Returns an empty sequence if not subscribed.

        Example:
            ```python
            topics = subscriber.subscribed_topics
            for topic in topics:
                print(f"Listening to: {topic}")
            ```
        """
        ...

    async def subscribe(
        self,
        topics: Sequence[str],
        callback: DashboardEventCallback,
    ) -> None:
        """
        Subscribe to event topics for real-time dashboard updates.

        Establishes subscriptions to the specified topics and registers
        the callback to be invoked when events are received. The callback
        is called synchronously for each received event.

        Args:
            topics: Sequence of topic names to subscribe to.
                Common topics include:
                - "node.execution.started" - Node begins execution
                - "node.execution.completed" - Node finishes execution
                - "node.execution.failed" - Node execution error
                - "workflow.status.changed" - Workflow state transition
                - "metrics.threshold.exceeded" - Metric alert triggered
                - "system.health.changed" - System health update
            callback: Function to call when events are received.
                Signature: (topic: str, event_data: dict[str, Any]) -> None
                The callback receives the topic name and event payload.

        Raises:
            SPIError: If subscription to any topic fails.
            OSError: If unable to connect to the event bus.
            ValueError: If topics sequence is empty or callback is None.

        Example:
            ```python
            def handle_workflow_events(topic: str, data: dict[str, Any]) -> None:
                workflow_id = data.get("workflow_id")
                new_status = data.get("status")
                print(f"Workflow {workflow_id}: {new_status}")

            await subscriber.subscribe(
                topics=[
                    "workflow.status.changed",
                    "workflow.completed",
                    "workflow.failed"
                ],
                callback=handle_workflow_events
            )
            ```

        Note:
            Calling subscribe when already subscribed will replace the
            existing subscriptions with the new topics and callback.
            Call unsubscribe first if you need to cleanly stop existing
            subscriptions before starting new ones.
        """
        ...

    async def unsubscribe(self) -> None:
        """
        Unsubscribe from all currently subscribed topics.

        Removes all active subscriptions and stops event delivery to
        the callback. After calling this method, is_subscribed will
        return False and subscribed_topics will return an empty sequence.

        This method is idempotent - calling it when not subscribed
        has no effect and does not raise an error.

        Raises:
            ConnectionError: If unable to communicate with the event bus
                during unsubscription.

        Example:
            ```python
            # Graceful shutdown pattern
            try:
                # ... process events ...
            finally:
                await subscriber.unsubscribe()
                print("Unsubscribed from all topics")
            ```

        Note:
            Any events that are in-flight during unsubscription may still
            be delivered to the callback. Implementations should ensure
            the callback remains valid until unsubscribe returns.
        """
        ...
