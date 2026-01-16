"""Protocol interface for Workflow event coordinator tools in ONEX systems.

This module defines the interface for tools that coordinate event-driven workflow
execution with strict SPI purity compliance. The coordinator manages the flow of
workflow events, triggers state transitions, and tracks event processing status.

Key Capabilities:
    - Event-driven workflow coordination
    - Event bus integration for publish/subscribe
    - State transition management
    - Event status tracking and monitoring
    - Registry integration for tool access
    - Health monitoring and diagnostics

Example:
    ```python
    from omnibase_spi.protocols.workflow_orchestration import (
        ProtocolWorkflowEventCoordinator
    )

    # Get coordinator from dependency injection
    coordinator: ProtocolWorkflowEventCoordinator = get_workflow_event_coordinator()

    # Set up dependencies
    coordinator.set_registry(registry)
    coordinator.set_event_bus(event_bus)

    # Coordinate workflow events
    event = create_workflow_event(
        event_type="task.completed",
        workflow_type="data_processing",
        instance_id=uuid.uuid4()
    )

    result = await coordinator.coordinate_events(
        workflow_events=[event],
        scenario_id="scenario-123",
        correlation_id=str(uuid.uuid4())
    )

    # Check event status
    status = await coordinator.get_event_status("event-456")
    print(f"Event status: {status}")
    ```

See Also:
    - ProtocolWorkflowEventBus: Event bus for workflow operations.
    - ProtocolWorkflowEvent: Workflow event structure.
    - ProtocolNodeRegistry: Registry for accessing tools.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue

if TYPE_CHECKING:
    from omnibase_spi.protocols.event_bus.protocol_event_bus_mixin import (
        ProtocolEventBusBase,
    )
    from omnibase_spi.protocols.node.protocol_node_registry import ProtocolNodeRegistry
    from omnibase_spi.protocols.types.protocol_file_handling_types import (
        ProtocolResult,
    )
    from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import (
        ProtocolWorkflowEvent,
    )


@runtime_checkable
class ProtocolWorkflowEventCoordinator(Protocol):
    """
    Protocol for Workflow event coordinator tools that manage event-driven
    workflow coordination in ONEX systems.

    These tools handle the coordination of events, triggers, and state
    transitions within workflow execution with strict SPI purity compliance.

    Key Features:
        - Event-driven workflow coordination
        - Event bus integration for publish/subscribe
        - State transition management
        - Event status tracking and monitoring
        - Registry integration for tool access

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        coordinator: ProtocolWorkflowEventCoordinator = get_workflow_event_coordinator()

        # Set up registry and event bus
        registry: "ProtocolNodeRegistry" = get_node_registry()
        event_bus: "ProtocolEventBus" = get_event_bus()

        coordinator.set_registry(registry)
        coordinator.set_event_bus(event_bus)

        # Create workflow event
        event: "ProtocolWorkflowEvent" = create_workflow_event(
            event_type="task.completed",
            workflow_type="data_processing",
            instance_id=uuid.uuid4()
        )

        # Coordinate events
        result = coordinator.coordinate_events(
            workflow_events=[event],
            scenario_id="scenario-123",
            correlation_id=str(uuid.uuid4())
        )

        # Check event status
        status = coordinator.get_event_status("event-456")
        ```
    """

    def set_registry(self, registry: "ProtocolNodeRegistry") -> None:
        """Set the registry for accessing other tools and dependencies.

        Args:
            registry: The registry containing other tools and dependencies.

        Raises:
            ConfigurationError: If registry is invalid or incompatible.
        """
        ...

    def set_event_bus(self, event_bus: "ProtocolEventBusBase") -> None:
        """Set the event bus for publishing and subscribing to events.

        Args:
            event_bus: The event bus instance for event distribution.

        Raises:
            ConfigurationError: If event bus is invalid or not connected.
        """
        ...

    async def run(self, input_state: dict[str, ContextValue]) -> "ProtocolResult":
        """Run the Workflow event coordinator with the provided input state.

        Args:
            input_state: Input state containing action and parameters for event coordination.

        Returns:
            Result of event coordination including status and output data.

        Raises:
            CoordinatorNotConfiguredError: If registry or event bus not set.
            ExecutionError: If coordination execution fails.
        """
        ...

    async def coordinate_events(
        self,
        workflow_events: list["ProtocolWorkflowEvent"],
        scenario_id: str,
        correlation_id: str,
    ) -> "ProtocolResult":
        """Coordinate a list of workflow events.

        Args:
            workflow_events: List of workflow events to coordinate.
            scenario_id: ID of the scenario.
            correlation_id: Correlation ID for tracking and debugging.

        Returns:
            Result of event coordination including success status and any errors.

        Raises:
            CoordinationError: If event coordination fails.
            ValidationError: If workflow events are invalid.
        """
        ...

    async def publish_workflow_event(
        self,
        event: "ProtocolWorkflowEvent",
        correlation_id: str,
    ) -> "ProtocolResult":
        """Publish a workflow event to the event bus.

        Args:
            event: Workflow event to publish.
            correlation_id: Correlation ID for tracking and debugging.

        Returns:
            Result of event publishing including delivery status.

        Raises:
            PublishError: If event publication fails.
            EventBusNotConfiguredError: If event bus is not set.
        """
        ...

    async def subscribe_to_events(
        self,
        event_types: list[str],
        callback: Callable[..., None],
        correlation_id: str,
    ) -> "ProtocolResult":
        """Subscribe to specific event types.

        Args:
            event_types: List of event types to subscribe to.
            callback: Callback function to handle events when they occur.
            correlation_id: Correlation ID for tracking and debugging.

        Returns:
            Result of event subscription including subscription ID.

        Raises:
            SubscriptionError: If subscription setup fails.
            EventBusNotConfiguredError: If event bus is not set.
        """
        ...

    async def get_event_status(self, event_id: str) -> dict[str, ContextValue] | None:
        """Get the status of a specific event.

        Args:
            event_id: ID of the event to query.

        Returns:
            Event status information or None if event not found.

        Raises:
            QueryError: If status query fails due to system error.
        """
        ...

    async def health_check(self) -> dict[str, ContextValue]:
        """Perform health check for the Workflow event coordinator.

        Returns:
            Health check result with status, capabilities, and performance metrics.
            Includes keys: "status", "capabilities", "event_bus_connected",
            "registry_configured", "last_event_processed".

        Raises:
            HealthCheckError: If health check cannot be performed.
        """
        ...
