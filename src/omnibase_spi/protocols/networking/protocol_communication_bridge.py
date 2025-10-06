"""
Protocol for Communication Bridge between ONEX and Claude Code agents.

This protocol defines the interface for bidirectional communication,
message routing, event streaming, and protocol translation between
ONEX and external agent systems.

Domain: Networking - External communication protocols
"""

from typing import TYPE_CHECKING, Any, AsyncIterator, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue
    from omnibase_spi.protocols.types.protocol_event_bus_types import ProtocolOnexEvent


@runtime_checkable
class ProtocolBridgeAgentMessage(Protocol):
    """Protocol for bridge agent event data."""

    event_type: str
    agent_id: str
    timestamp: float
    data: dict[str, "ContextValue"]


@runtime_checkable
class ProtocolBridgeProgressUpdate(Protocol):
    """Protocol for agent progress update data."""

    agent_id: str
    progress: float
    message: str
    timestamp: float


@runtime_checkable
class ProtocolBridgeWorkResult(Protocol):
    """Protocol for agent work result data."""

    agent_id: str
    success: bool
    files: list[str]
    output: str
    timestamp: float


@runtime_checkable
class ProtocolBridgeOnexEvent(Protocol):
    """Protocol for bridge ONEX event data."""

    event_type: str
    source: str
    timestamp: float
    data: dict[str, "ContextValue"]


@runtime_checkable
class ProtocolAgentWorkTicket(Protocol):
    """Protocol for agent work ticket data."""

    ticket_id: str
    agent_id: str
    work_type: str
    parameters: dict[str, "ContextValue"]
    priority: int
    created_at: float


@runtime_checkable
class ProtocolCommunicationBridge(Protocol):
    """
    Protocol for ONEX <-> external agent communication bridge.

    Provides bidirectional communication, message routing, event streaming,
    and protocol translation between ONEX and external agent systems.

    Example:
        ```python
        # Implementation example (not part of SPI)
        # All methods defined in the protocol contract must be implemented

        # Usage in application
        bridge: "ProtocolCommunicationBridge" = get_communication_bridge()

        # Register agent
        await bridge.register_agent("agent-001", "http://localhost:8080")

        # Forward work request
        ticket = ProtocolAgentWorkTicket(
            ticket_id="ticket-123",
            agent_id="agent-001",
            work_type="data_processing",
            parameters={"input_file": "/data/input.csv"},
            priority=1,
            created_at=time.time()
        )

        success = await bridge.forward_work_request("agent-001", ticket)
        if success:
            print("Work request forwarded successfully")

        # Subscribe to events
        async for event in bridge.subscribe_to_agent_events("agent-001"):
            print(f"Received event: {event.event_type}")
            await handle_agent_event(event)

        # Send commands
        await bridge.send_agent_command("agent-001", "pause")
        await bridge.send_agent_command("agent-001", "resume", {"speed": "fast"})

        # Check connectivity
        is_connected = await bridge.check_agent_connectivity("agent-001")
        print(f"Agent connectivity: {is_connected}")

        # Get statistics
        stats = await bridge.get_message_statistics()
        print(f"Message statistics: {stats}")
        ```

    Communication Patterns:
        - Work request forwarding with ticket-based tracking
        - Agent command and control with parameter support
        - Event streaming for real-time monitoring
        - Bidirectional message transformation
        - Health monitoring and connectivity checking
        - Statistical tracking and reporting
    """

    async def forward_work_request(
        self,
        agent_id: str,
        ticket: "ProtocolAgentWorkTicket",
    ) -> bool:
        """
        Forward work request from ONEX to external agent.

        Args:
            agent_id: Target agent identifier
            ticket: Work ticket to be processed

        Returns:
            True if request was successfully forwarded

        Raises:
            CommunicationError: If forwarding fails
            AgentNotFoundError: If agent is not available
        """
        ...

    async def send_agent_command(
        self,
        agent_id: str,
        command: str,
        parameters: dict[str, str] | None = None,
    ) -> bool:
        """
        Send command to specific external agent.

        Args:
            agent_id: Target agent identifier
            command: Command to execute (start, stop, pause, resume)
            parameters: Optional command parameters

        Returns:
            True if command was successfully sent

        Raises:
            CommunicationError: If command sending fails
            InvalidCommandError: If command is not recognized
        """
        ...

    async def receive_progress_update(
        self, update: "ProtocolBridgeProgressUpdate"
    ) -> None:
        """
        Receive progress update from external agent.

        Args:
            update: Progress update information

        Raises:
            ProcessingError: If update processing fails
        """
        ...

    async def receive_work_completion(self, result: "ProtocolBridgeWorkResult") -> None:
        """
        Receive work completion notification from external agent.

        Args:
            result: Work completion result with files and status

        Raises:
            ProcessingError: If result processing fails
        """
        ...

    async def receive_agent_event(self, event: "ProtocolBridgeAgentMessage") -> None:
        """
        Receive general event from external agent.

        Args:
            event: Agent event information

        Raises:
            ProcessingError: If event processing fails
        """
        ...

    async def subscribe_to_agent_events(
        self,
        agent_id: str,
    ) -> "AsyncIterator[ProtocolBridgeAgentMessage]":
        """
        Subscribe to event stream from specific external agent.

        Args:
            agent_id: Agent to subscribe to

        Yields:
            Agent events as they occur

        Raises:
            SubscriptionError: If subscription fails
        """
        ...

    async def publish_to_event_bus(self, event: "ProtocolOnexEvent") -> bool:
        """
        Publish event to ONEX Event Bus.

        Args:
            event: ONEX event to publish

        Returns:
            True if event was successfully published

        Raises:
            PublishError: If publishing fails
        """
        ...

    async def subscribe_to_onex_events(
        self,
        event_types: list[str],
    ) -> "AsyncIterator[ProtocolOnexEvent]":
        """
        Subscribe to ONEX Event Bus for specific event types.

        Args:
            event_types: List of event types to subscribe to

        Yields:
            ONEX events as they occur

        Raises:
            SubscriptionError: If subscription fails
        """
        ...

    async def register_agent(self, agent_id: str, endpoint_url: str) -> bool:
        """
        Register external agent with communication bridge.

        Args:
            agent_id: Unique agent identifier
            endpoint_url: Agent's communication endpoint

        Returns:
            True if registration was successful

        Raises:
            RegistrationError: If registration fails
        """
        ...

    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister external agent from communication bridge.

        Args:
            agent_id: Agent identifier to unregister

        Returns:
            True if unregistration was successful

        Raises:
            UnregistrationError: If unregistration fails
        """
        ...

    async def get_registered_agents(self) -> list[str]:
        """
        Get list of currently registered agents.

        Returns:
            List of registered agent IDs
        """
        ...

    async def check_agent_connectivity(self, agent_id: str) -> bool:
        """
        Check connectivity to specific external agent.

        Args:
            agent_id: Agent to check connectivity for

        Returns:
            True if agent is reachable
        """
        ...

    async def get_message_statistics(self) -> dict[str, int]:
        """
        Get communication statistics.

        Returns:
            Dictionary of message counts and statistics
        """
        ...

    async def transform_onex_to_agent_message(
        self,
        onex_event: "ProtocolOnexEvent",
    ) -> dict[str, str] | None:
        """
        Transform ONEX event to external agent message format.

        Args:
            onex_event: ONEX event to transform

        Returns:
            Transformed message or None if not applicable
        """
        ...

    async def transform_agent_to_onex_event(
        self,
        agent_event: "ProtocolBridgeAgentMessage",
    ) -> "ProtocolOnexEvent" | None:
        """
        Transform external agent event to ONEX event format.

        Args:
            agent_event: Agent event to transform

        Returns:
            Transformed ONEX event or None if not applicable
        """
        ...
